from flask import jsonify
from . import api
from app.exceptions import ValidationError


# 除404,500错误外，其他错误由Web服务生成，故可在蓝本中以辅助函数的形式实现
def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def method_not_allowed(message):
    response = jsonify({'error': 'method not allow', 'message': message})
    response.status_code = 405
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])