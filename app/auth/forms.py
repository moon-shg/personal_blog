from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User, Role


class RenderForm(FlaskForm):
    class Meta(FlaskForm.Meta):
        """
        重写render_field，实现Flask-Bootstrap与render_kw的class并存
        """
        def render_field(self, field, render_kw):
            other_kw = getattr(field, 'render_kw', None)
            if other_kw is not None:
                class1 = other_kw.get('class', None)
                class2 = render_kw.get('class', None)
                if class1 and class2:
                    render_kw['class'] = class2 + ' ' + class1
                render_kw = dict(other_kw, **render_kw)
            return field.widget(field, **render_kw)


# 登录表单
class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField()


# 注册表单
class RegistrationForm(RenderForm):
    email = StringField(label='邮箱地址', validators=[DataRequired(), Length(1, 64), Email(message="请输入有效的邮箱")])
    username = StringField(label='用户名',
        validators=[DataRequired(), Length(1, 64), Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0, "用户名只能使用数字字母和下划线~")])
    password_1 = PasswordField(label='密码', validators=[DataRequired(), EqualTo("password_2", message="两次密码不相同")])
    password_2 = PasswordField(label='确认密码', validators=[DataRequired()])
    submit = SubmitField(render_kw={"value":"注册", 'class':"btn btn-block u-btn-primary g-font-size-16 g-py-10 border-0 g-my-30"})

    # 如果表单类中定义了 以 validate_filedname 为名的方法，这个方法就会和常规的验证函数一起调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册！')


# 修改密码表单
class ChangePasswordForm(RenderForm):
    old_psd = PasswordField(label="旧密码", validators=[DataRequired()])
    new_psd1 = PasswordField(label='新密码', validators=[DataRequired(), EqualTo("new_psd2", message="两次密码不相同")])
    new_psd2 = PasswordField(label='确认新密码', validators=[DataRequired()])
    submit = SubmitField(render_kw={"value":"确认修改", 'class':"btn btn-block u-btn-primary g-font-size-16 g-py-10 border-0 g-my-30"})


# 重置密码请求表单
class ResetPasswordRequestForm(RenderForm):
    email = StringField(label='', validators=[DataRequired(), Length(1, 64), Email(message="请输入有效的邮箱")],
                        render_kw={'class':'form-control form-control-lg g-pa-15', 'placeholder':"邮箱地址"})
    submit = SubmitField(render_kw={"value":"提交", 'class':"btn btn-block u-btn-primary g-font-size-16 g-py-10 border-0 g-my-30"})


# 重置密码表单
class ResetPasswordForm(RenderForm):
    new_psd1 = PasswordField(label='新密码', validators=[DataRequired(), EqualTo("new_psd2", message="两次密码不相同")])
    new_psd2 = PasswordField(label='确认新密码', validators=[DataRequired()])
    submit = SubmitField(render_kw={"value":"确认修改", 'class':"btn btn-block u-btn-primary g-font-size-16 g-py-10 border-0 g-my-30"})
