from ..main.forms import RenderForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostEditForm(RenderForm):
    title = StringField(label='标题', validators=[DataRequired(), Length(1, 255)])
    summary = StringField(label='概述')
    body = TextAreaField(label="正文", validators=[DataRequired()],
                         render_kw={'data-provide': "markdown", 'rows': '10',
                                    "placeholder": "文章正文(支持MarkDown)",
                                    'class': "form-control form-control-md g-color-black g-bg-white--focus g-brd-gray-light-v4 g-brd-primary--focus g-resize-none rounded-3 g-pa-15"})
    submit = SubmitField(label='提交')