from ..auth.forms import RenderForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField, SelectField, RadioField, ValidationError
from wtforms.validators import Length, DataRequired, Email, Regexp
from ..models import Role, User


# 编辑个人资料表单
class EditProfileForm(RenderForm):
    name = StringField(validators=[Length(0, 64)])
    gender = SelectField(coerce=int, choices=[(1, '男'), (0, '女')])
    location = StringField(validators=[Length(0, 64)])
    about_me = TextAreaField()
    submit = SubmitField()


# 管理员用编辑资料表单
class EditProfileAdminForm(RenderForm):
    email = StringField(validators=[DataRequired(), Length(1, 64), Email(message="请输入有效的邮箱")])
    username = StringField(validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0, "用户名只能使用数字字母和下划线~")])
    confirmed = BooleanField()
    role = SelectField(coerce=int)
    name = StringField(validators=[Length(0, 64)])
    gender = SelectField(coerce=int, choices=[(1, '男'), (0, '女')])
    location = StringField(validators=[Length(0, 64)])
    about_me = TextAreaField()
    submit = SubmitField()

    # 添加 用户组选择表单role 的值
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user  # 表单接收用户作为参数，以便在自定义的验证方法如validate_email中能够使用变量user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')
