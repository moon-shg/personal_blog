from ..auth.forms import RenderForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import Length


# 编辑个人资料表单
class EditProfileForm(RenderForm):
    name = StringField(validators=[Length(0, 64)])
    gender = BooleanField()
    location = StringField(validators=[Length(0, 64)])
    about_me = TextAreaField()
    submit = SubmitField()
