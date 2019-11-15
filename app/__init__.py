from flask import Flask


def create_app():
    # 初始化应用
    app = Flask(__name__)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
