from flask import render_template
from . import main
from app import db
from .forms import PostForm
from flask_login import current_user
from ..models import User, Role, Permission, Post

# 主页面
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(
            title=form.title.data,
            summary=form.summary.data,
            body=form.body.data,
            author=current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)
