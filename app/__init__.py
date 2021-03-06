from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_uploads import UploadSet, configure_uploads, patch_request_class
from flask_ckeditor import CKEditor
from flask_toastr import Toastr
import flask_whooshalchemyplus


bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 设置登录页面的 endpiont
avatars = UploadSet('AVATAR')
post_img = UploadSet('POSTIMG')
ckeditor = CKEditor()
toastr = Toastr()


def create_app(config_name):
    # 初始化应用
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    # 配置flask-uploads
    configure_uploads(app, (avatars, post_img))
    patch_request_class(app, 3*1024*1024)  # 设置上传文件最大为2mb
    ckeditor.init_app(app)
    toastr.init_app(app)
    flask_whooshalchemyplus.init_app(app)


    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .user import user_page as user_page_blueprint
    app.register_blueprint(user_page_blueprint, url_prefix='/user')

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint, url_prefix='/blog')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
