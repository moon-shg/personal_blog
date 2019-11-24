import os
from app import create_app, db
from app.models import User, Role, Permission, Post
from flask_migrate import Migrate


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

# 注册上下文处理器，为shell导入数据库相关信息
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post)

# 在cli中添加启动单元测试的命令
@app.cli.command()
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)