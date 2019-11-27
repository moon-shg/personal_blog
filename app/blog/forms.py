from ..main.forms import RenderForm
from wtforms import SubmitField, StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from ..models import Category


# 文章修改
class PostEditForm(RenderForm):
    title = StringField(label='标题', validators=[DataRequired(), Length(1, 255)])
    summary = StringField(label='概述')
    category = SelectField(label="文章分类", coerce=int)
    body = TextAreaField(label="正文", validators=[DataRequired()],
                         render_kw={'data-provide': "markdown", 'rows': '10',
                                    "placeholder": "文章正文(支持MarkDown)",
                                    'class': "form-control form-control-md g-color-black g-bg-white--focus g-brd-gray-light-v4 g-brd-primary--focus g-resize-none rounded-3 g-pa-15"})
    submit = SubmitField(label='提交')

    # 添加 分类选择表单category 的值
    def __init__(self, *args, **kwargs):
        super(PostEditForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in
                                 Category.query.order_by(Category.default.desc()).all()]


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
