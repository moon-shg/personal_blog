from flask import Blueprint

blog = Blueprint('blog', __name__)

from . import views
from ..models import Permission


# 添加应用上下文处理器，使得渲染时，模板中能够直接调用Permission类而无需导入
@blog.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
