import os
from flask_uploads import IMAGES
import mysql.connector

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Potato Cookbook')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    # MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER', 'ST<393773661@QQ.COM>')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 设置分页
    POSTS_PER_PAGE = int(os.environ.get('POSTS_PER_PAGE', '10'))
    # flask-uploads 配置
    # 用户头像文件
    UPLOADED_AVATAR_DEST = os.path.join(basedir, 'app/static/img/upload')
    UPLOADED_AVATAR_ALLOW = IMAGES
    # 文章头图
    UPLOADED_POSTIMG_DEST = os.path.join(basedir, 'app/static/img/upload/post_img')
    UPLOADED_POSTIMG_ALLOW = IMAGES


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


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
