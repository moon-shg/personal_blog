from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission, Category


# 添加应用上下文处理器，使得渲染时，模板中能够直接调用Permission类而无需导入
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

# 添加应用上下文处理器，使得渲染时，模板中能够直接调用Category类而无需导入
@main.app_context_processor
def inject_categories():
    return dict(Category=Category)