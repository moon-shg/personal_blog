from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    # 由于404错误是由Flask自己生成的，而且一般会返回HTML响应。所以这里需要为 API 写 JSON 格式的 response
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404


@main.errorhandler(500)
def internal_server_error(e):
    # 同404错误，为 API 写 JSON 格式的 response
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500


@main.errorhandler(403)
def forbidden_error(e):
    return render_template('errors/403.html'), 403
