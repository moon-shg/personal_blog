from . import db, login_manager
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from markdown import markdown
import bleach
from jieba.analyse.analyzer import ChineseAnalyzer
import flask_whooshalchemyplus


# 用户组权限
class Permission:
    FOLLOW = 1
    COMMENT = 16
    WRITE = 128
    MODERATE = 512
    ADMIN = 1024


# 用户组
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    # 用户权限
    # 判断是否有权限
    def has_permission(self, perm):
        # 用位运算符（按位与）来判断是否有权限。
        # 因为 premission 用 2^n 数字表示，所以 permission 二进制数的每一位都能表示一个权限
        return self.permissions & perm == perm

    # 添加权限
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    # 移除权限
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    # 重置权限
    def reset_permission(self):
        self.permissions = 0

    # 创建实例时初始化权限
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    # 在数据库中创建各个用户组，并初始化各个用户组的权限
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT],
            'PrimeUser': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            # 为每个用户组添加相应权限
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)  # 当前用户组为默认用户组‘User’时，设置role.default值为True
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f'<用户组：{self.name}>'


# 用户
# 通过添加父类UserMixin,来继承Flask_login的一些属性和方法（如：is_authenticated, is_active, is_anonymous 和 get_id()）
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    # 个人资料
    name = db.Column(db.Unicode(64))
    location = db.Column(db.Unicode(64))
    gender = db.Column(db.Boolean, default=True)
    about_me = db.Column(db.UnicodeText())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 头像
    avatar = db.Column(db.String(128), default='/static/img/avatar/akkarin.jpg')
    # 博客
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 评论
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    # 收藏文章
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    # 创建用户时，设置默认用户组
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    # 将密码设置为只写属性
    @property
    def password(self):
        raise AttributeError('password is not readalbe attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成邮箱验证令牌token
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'confirm': self.id}).decode('utf-8')
        return token

    # 校验邮箱验证令牌token
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # 生成重置密码令牌token
    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        token = s.dumps({'reset': self.id}).decode('utf-8')
        return token

    # 校验重置密码令牌token
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    # 判断用户权限
    def can(self, perm):
        return self.role.has_permission(perm)

    def is_administrator(self):
        return self.role.has_permission(Permission.ADMIN)

    # 登录时，刷新last_seen属性 (另见auth/views.py)
    def refresh_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<用户名：{self.username}>'

    # 收藏文章
    def like(self, post):
        if not self.liked(post):
            l = Like(user=self, post=post)
            db.session.add(l)

    # 取消收藏
    def dislike(self, post):
        if self.liked(post):
            l = self.likes.filter_by(post_id=post.id).first()
            if l:
                db.session.delete(l)

    def liked(self, post):
        if post.id is None:
            return False
        return self.likes.filter_by(post_id=post.id).first() is not None


# 匿名用户
class AnonymousUser(AnonymousUserMixin):
    # 定义匿名用户权限
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


# Flask-login 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 博客
class Post(db.Model):
    __tablename__ = 'posts'
    __searchable__ = ['body', 'title', 'summary']  # 设定可以用于搜索的字段
    __analyzer__ = ChineseAnalyzer()  # 搜索的中文支持。添加本地自定义分析器进行索引
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    summary = db.Column(db.UnicodeText)
    body = db.Column(db.UnicodeText)
    body_html = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 分类
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    # 评论
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # 被收藏
    liked = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    # 文章头图
    image = db.Column(db.String(128))

    # 创建博客时，设置默认分类
    def __int__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        if self.category is None:
            self.category = Category.query.filter_by(default=True).first()

    # 在服务器端将post.body中的markdown文本转换成html格式
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # 设置bleach.clean 允许的标签
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']
        # 设置bleach.clean 允许的属性
        allowed_attr = {
            'a': ['href', 'title'],
            'abbr': ['title'],
            'acronym': ['title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=allowed_attr, strip=True))

    # 被收藏
    def is_liked_by(self, user):
        if user.id is None:
            return False
        return self.liked.filter_by(user_id=user.id).first() is not None

    def __repr__(self):
        return f'<文章：{self.title}>'

# SQLAlchemy ‘set’事件监听程序，当body字段设了新值，函数就会自动被调用。
db.event.listen(Post.body, 'set', Post.on_changed_body)


# 博客文章分类
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    default = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    # 二级分类
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sub_categories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    posts_sub = db.relationship('Post', backref='sub_category', lazy='dynamic')

    # 添加文章分类
    @staticmethod
    def add_category(new_category):
        category = Category.query.filter_by(name=new_category).first()
        if category is None:
            category = Category(name=new_category)
            db.session.add(category)
            db.session.commit()

    def __repr__(self):
        return f'<文章分类： {self.name}>'


# 评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.UnicodeText)
    body_html = db.Column(db.UnicodeText)
    disable = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    # 评论回复 (一对多的自引用，也是树状结构)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic')  # 这里使用 remote_side 表示多对一的关系

    # 在服务器端将comment.body中的markdown文本转换成html格式
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # 设置bleach.clean 允许的标签
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em',
                        'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img']
        # 设置bleach.clean 允许的属性
        allowed_attr = {
            'a': ['href', 'title'],
            'abbr': ['title'],
            'acronym': ['title'],
            'img': ['src', 'alt', 'title', 'width', 'height']
        }
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, attributes=allowed_attr, strip=True))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# 收藏文章
class Like(db.Model):
    __tablename__ = 'likes'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
