import os
from app import create_app, db
from flask import redirect, url_for
from app.models import User, Role, Permission, Post, Category, Comment
from flask_migrate import Migrate, upgrade
from flask_script import Manager

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)


@app.route('/main')
def index():
    return redirect(url_for('main.index'))


# 注册上下文处理器，为shell导入数据库相关信息
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Category=Category, Comment=Comment)


# 在cli中添加启动单元测试的命令
@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def hello():
    """一个测试命令"""
    print('Hello!')
    return "Hello World!"


# 部署
@app.cli.command()
def deploy():
    """Run deployment tasks"""
    # 把数据库迁移到最新版本
    db.create_all()

    # 创建或更新用户组
    Role.insert_roles()

    # 创建或更新分类
    Category.insert_category()
