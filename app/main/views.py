from flask import render_template
from . import main

# 主页面
@main.route('/')
def index():
    return render_template('index.html')