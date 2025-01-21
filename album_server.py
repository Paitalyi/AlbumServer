#!/usr/bin/env python
from flask import Flask, request, render_template, send_file, redirect, url_for, session, send_from_directory, abort, jsonify, flash
import os
import time
from sys import argv
from random import choice
from watchdog.observers import Observer
from album_utils import *

# Flask 应用初始化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 用于保护会话信息
app.config.from_pyfile('config.py')

# 默认值
PORT = 8888
HOME_DIR = r"D:\图片"

# 尝试获取port和home_dir参数
custom_port = None
custom_home_dir = None
try:
    custom_port = int(argv[1])
    custom_home_dir = argv[2]
except:
    pass
port = custom_port or PORT
home_dir = custom_home_dir or HOME_DIR

# 文件处理器实例
file_handler = GalleryFileHandler(home_dir)
# test
print(f'Show gallery in [{home_dir}].')

# 节流器
def sort_subdir4home_dir(file_handler):
    file_handler.subdirectories4home_dir.sort(key=lambda x: list(map(ord, x)))
    # test
    print('Call throttled func')
throttler = Throttler(interval=2, func=sort_subdir4home_dir)  # 节流器 间隔2s

# 事件处理器实例
event_handler = DirectoryEventHandler(file_handler, throttler)
# 观察者实例
observer = Observer()
# 开始监控
observer.schedule(event_handler, home_dir, recursive=False)
observer.start()
print(f'Monitoring directory: [{home_dir}].')
print('Pls use double Ctrl+C to stop.\n')

def safe_path_check(request_path):
    """
    安全检查 确保路径位于home_dir内
    """
    # 获取真实路径并与 home_dir 比较
    if request_path in ['', '/', '\\']:
        full_path = file_handler.home_dir
    else:
        full_path = os.path.abspath(os.path.join(file_handler.home_dir, request_path))

    # 确保 full_path 是 home_dir 下的路径
    if not full_path.startswith(file_handler.home_dir):
        abort(403)  # 如果路径不合法，返回403 Forbidden
    return full_path

@app.before_request
def check_login():
    # 如果用户没有登录且正在访问的不是登录页或登录成功后需要跳转的页面
    if 'user' not in session and request.endpoint not in ['login', 'static', 'favicon']:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('view_dir', path=''))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 获取配置文件中的管理员账号和密码
        admin_username = app.config['ADMIN_USERNAME']
        admin_password = app.config['ADMIN_PASSWORD']

        if username == admin_username and password == admin_password:
            session['user'] = username
            flash('登陆成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('登出成功', 'info')
    return redirect(url_for('index'))

@app.route('/view_dir')
def view_dir():
    relative_path = request.args.get('path', '')
    page = int(request.args.get('page', 1))
    
    # 安全检查
    full_path = safe_path_check(relative_path)

    if os.path.isdir(full_path):
        subdirectories = file_handler.get_subdirectories(full_path)
        if subdirectories:
            html_content = file_handler.generate_index_html(subdirectories, relative_path, page)
            file_handler.current_dir = full_path  # 为了实现搜索功能
            # test
            print(f'current_dir is [{file_handler.current_dir}].')
        else:
            image_files = file_handler.get_image_files(full_path)
            user_agent = request.headers.get('User-Agent', '')
            html_content = file_handler.generate_gallery_html(image_files, relative_path, page, user_agent)
        return html_content
    else:
        return "<h1>404 Directory not found.</h1>", 404

@app.route('/view_img')
def view_img():
    relative_path = request.args.get('path', '')

    # 安全检查
    full_path = safe_path_check(relative_path)

    if os.path.isfile(full_path) and is_img(full_path):
        return send_file(full_path)
    else:
        return "<h1>404 Image not found.</h1>", 404

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '')
    depth = request.form.get('depth', 'shallow')

    # 检查 query 是否为空
    if not query:
        return jsonify({"error": "Search query cannot be empty."}), 400

    search_results = file_handler.search_folders(query, depth)
    html_content = file_handler.generate_search_html(search_results, query)
    return html_content

@app.route('/random_subdir')
def random_subdirectory():
    # 获取当前目录的子目录
    relative_path = request.args.get('path', '')

    # 安全检查
    full_path = safe_path_check(relative_path)
    # test
    print(f"当前目录: [{full_path}] 开始获取子目录...")

    if os.path.isdir(full_path):
        subdirectories = file_handler.get_subdirectories(full_path)
        # test
        print(f"成功获取子目录 其长度为: <{len(subdirectories)}> 开始从中随机选择子目录...")
        if subdirectories:
            # 随机选择一个子目录
            random_dir = choice(subdirectories)
            # test
            print(f"随机选中: [{random_dir}]")
            return redirect(url_for('view_dir', path=random_dir))
        else:
            return "<h1>No subdirectories found.</h1>", 404
    else:
        return "<h1>Invalid directory path.</h1>", 404

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('./', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))  # 设置工作目录为脚本所在目录
    app.run(host='0.0.0.0', port=port)
    # 0.0.0.0 是一个通配地址，表示绑定到所有 IPv4 地址上的网络接口。
    # 无论是本地的 localhost (127.0.0.1)，还是服务器的公网 IP，都可以通过对应的地址访问这个 Flask 应用。

    # 平滑退出observer
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStop monitoring.")
    observer.join()
