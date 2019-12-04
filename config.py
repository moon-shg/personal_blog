import os
from flask_uploads import IMAGES
import mysql.connector

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Potato Cookbook')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER', 'Potato Cookbook<potato_support@163.com>')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 设置分页
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', '10'))
    # flask-uploads 配置
    # 用户头像文件
    UPLOADED_AVATAR_DEST = os.path.join(basedir, 'app/static/img/upload/avatar')
    UPLOADED_AVATAR_ALLOW = IMAGES
    # 文章头图
    UPLOADED_POSTIMG_DEST = os.path.join(basedir, 'app/static/img/upload/post_img')
    UPLOADED_POSTIMG_ALLOW = IMAGES
    # CKEditor
    CKEDITOR_FILE_UPLOADER = 'blog.upload'
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_EXTRA_PLUGINS = ['codesnippet', 'filebrowser', 'popup', 'filetools', 'markdown']
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_CODE_THEME = 'github'
    # 搜索 每页显示结果数
    SEARCH_RESULTS_PER_PAGE = int(os.environ.get('SEARCH_RESULTS_PER_PAGE', '7'))


    @staticmethod
    def init_app(app):
        pass


# 定义不同环境中的配置
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              "mysql+mysqlconnector://st:123456@localhost:3306/blog_dev?charset=utf8"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              "mysql+mysqlconnector://st:123456@localhost:3306/blog_test?charset=utf8"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
                              "mysql+mysqlconnector://st:123456@localhost:3306/blog_production?charset=utf8"

    # 应用出错时发送电子邮件
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 出错时邮件通知管理员
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.MAIL_SENDER],
            subject='Potato Web Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
