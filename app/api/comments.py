from . import api
from app.models import Comment, Permission
from flask import jsonify, g, request
from .decorators import permission_required
from .errors import forbidden
from app import db


# 获取一条评论
@api.route('/comment/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


# 修改一条评论
@api.route('/comment/<int:id>', methods=['PUT'])
@permission_required(Permission.COMMENT)
def edit_comment(id):
    comment = Comment.query.get_or_404(id)
    if g.current_user != comment.author:
        return forbidden('Insufficient permission')
    comment.body = request.json.get('body', comment.body)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())

# 封禁/解封一条评论
@api.route('/comment/<int:id>/disable/', methods=['POST'])
@permission_required(Permission.MODERATE)
def moderate_comment(id):
    comment = Comment.query.get_or_404(id)
    if request.json.get('disable').lower() in ['true', '1', 'on']:
        comment.disable = True
    elif request.json.get('disable').lower() in ['false', '0', 'off']:
        comment.disable = False
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())
