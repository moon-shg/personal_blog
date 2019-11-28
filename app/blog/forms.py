from ..main.forms import RenderForm
from wtforms import SubmitField, StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length
from ..models import Category


# 文章修改
class PostEditForm(RenderForm):
    image = FileField()
    title = StringField(label='标题', validators=[DataRequired(), Length(1, 255)])
    summary = StringField(label='概述')
    category = SelectField(label="文章分类", coerce=int)
    sub_category = SelectField(label="文章分类", coerce=int)
    body = TextAreaField(label="正文", validators=[DataRequired()],
                         render_kw={'data-provide': "markdown", 'rows': '10',
                                    "placeholder": "文章正文(支持MarkDown)",
                                    'class': "form-control form-control-md g-color-black g-bg-white--focus g-brd-gray-light-v4 g-brd-primary--focus g-resize-none rounded-3 g-pa-15"})
    submit = SubmitField(label='提交')

    # 添加 分类选择表单 category 的值
    def __init__(self, *args, **kwargs):
        super(PostEditForm, self).__init__(*args, **kwargs)
        self.category.choices = [(0, '')]  # 给表单设置初始空值，以触发表单onchange事件
        self.sub_category.choices = [(0, '')]
        for category in Category.query.order_by(Category.id).all():
            # 初始化时将一级分类和二级分类区分开，分别给两个字段初始化
            if category.parent is None:
                self.category.choices.append((category.id, category.name))
            else:
                self.sub_category.choices.append((category.id, category.name))


# 发表评论&回复
class CommentForm(RenderForm):
    body = TextAreaField(label="正文", validators=[DataRequired()],
                         render_kw={'data-provide': "markdown", 'rows': '6',
                                    "placeholder": "发表评论(支持MarkDown)",
                                    'class': "form-control form-control-md g-color-black g-bg-white--focus g-brd-gray-light-v4 g-brd-primary--focus g-resize-none rounded-3 g-pa-15"})
    parent = StringField(label="被回复评论的id",
                         render_kw={'readonly': '', 'class': 'g-pos-abs g-top-0 invisible'})
    submit_comment = SubmitField(label='提交')


# 修改评论
class CommentEditForm(RenderForm):
    body = TextAreaField(label="正文", validators=[DataRequired()],
                         render_kw={'data-provide': "markdown", 'rows': '6',
                                    'class': "form-control form-control-md g-color-black g-bg-white--focus g-brd-gray-light-v4 g-brd-primary--focus g-resize-none rounded-3 g-pa-15"})
    id = StringField(label="自己的id",
                     render_kw={'readonly': '', 'class': 'g-pos-abs g-top-0 invisible'})
    submit_edit_comment = SubmitField(label='提交')


# 收藏文章
class LikePostForm(RenderForm):
    submit_like_post = SubmitField()

# 取消收藏
class DislikePostForm(RenderForm):
    submit_dislike_post = SubmitField()