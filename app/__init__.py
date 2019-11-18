from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name):
    # 初始化应用
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
