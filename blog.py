import os
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

# 注册上下文处理器，为shell导入数据库相关信息
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)