#!/usr/bin/env python
from flask import Flask, request, render_template, send_file, redirect, url_for, session, send_from_directory, abort, jsonify, flash
import os
import time
import argparse
from random import choice
from urllib.parse import quote
from album_utils import *

start_time = time.time()

# Flask 应用初始化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 用于保护会话信息
app.config.from_pyfile('config.py')

# 默认值
PORT = 8888
HOME_DIR = r"D:\图片"
ITEMS_PER_PAGE = 100
IMGS_PER_PAGE = 24

# 获取参数
parser = argparse.ArgumentParser()

parser.add_argument('--port', type=int, default=PORT, help='服务器监听的端口号')
parser.add_argument('--home', type=str, default=HOME_DIR, help='服务器展示的家目录')
parser.add_argument('--items', type=int, default=ITEMS_PER_PAGE, help='目录页每页的条目数')
parser.add_argument('--imgs', type=int, default=IMGS_PER_PAGE, help='图片页每页的图片数')

args = parser.parse_args()

port = args.port
home_dir = args.home
items_per_page = args.items
imgs_per_page = args.imgs

# 文件处理器实例
file_handler = GalleryFileHandler(home_dir)
print(Fore.GREEN + f'Show galleries in [{home_dir}].')

# 节流器
def sort_index(item_index, timers):
    item_index.sort(key=lambda x: list(map(ord, x)))
    print(Fore.GREEN + f'Sort index of timer: {id(item_index)}')
    del timers[id(item_index)]  # 删除对应的计时器
    print(Fore.YELLOW + f'Deleted timer: {id(item_index)}.')
throttler = Throttler(interval=5, func=sort_index)  # 节流器 延时5s

# 事件处理器实例
event_handler = DirectoryEventHandler(file_handler, throttler)
# 观察者实例
observer = DirectoryOnlyObserver()
# 开始监控
observer.schedule(event_handler, home_dir, recursive=True)
observer.start()
print(Fore.GREEN + f'Monitoring directory: [{home_dir}].')

end_time = time.time()
elapsed_time = end_time - start_time
print(Fore.CYAN + f'Initialization took {elapsed_time:.6f} seconds.')
print(Fore.CYAN + 'Pls use double Ctrl+C to stop.\n')


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

# 定义basename过滤器函数
def basename_filter(value):
    """提取文件路径中的文件名"""
    return os.path.basename(value)

# 使用装饰器注册basename过滤器
@app.template_filter('basename')
def register_basename_filter(value):
    return basename_filter(value)

@app.before_request
def check_login():
    # 如果用户没有登录且正在访问的不是登录页或登录成功后需要跳转的页面
    if 'user' not in session and request.endpoint not in ['login', 'favicon', 'static']:
        return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('view_dir', path=''))

@app.route('/settings')
def settings():
    return render_template('settings.html')

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
            search_query = ""
            total_subdirectories = len(subdirectories)
            total_pages = (total_subdirectories + items_per_page - 1) // items_per_page
            start_index = (page - 1) * items_per_page
            end_index = start_index + items_per_page
            subdirectories_to_display = subdirectories[start_index:end_index]

            if relative_path == '':
                relative_path = '/'

            file_handler.current_dir = full_path  # 为了实现搜索功能
            print(Fore.YELLOW + f'当前目录为 [{file_handler.current_dir}]')

            return render_template('index.html', title=f"当前目录: {relative_path}", query=search_query, path=relative_path, subdirectories=subdirectories_to_display, total_pages=total_pages, page=page)
        else:
            image_files = file_handler.get_image_files(full_path)
            user_agent = request.headers.get('User-Agent', '')

            # 获取当前文件夹的名称 relative_path即images的父目录
            folder_name = os.path.basename(relative_path)
            total_images = len(image_files)
            total_pages = (total_images + imgs_per_page - 1) // imgs_per_page
            start_index = (page - 1) * imgs_per_page
            end_index = start_index + imgs_per_page
            images_to_display = image_files[start_index:end_index]
            is_mobile_flag = is_mobile(user_agent)

            # 确保 relative_path 即image的父目录相对home_dir的相对路径在 cache_folders 中
            if relative_path not in file_handler.cache_folders:
                print(Fore.RED + f"Warning: [{relative_path}] not found in cache_folders.")
                cache_dir = os.path.relpath(file_handler.cache_folders_dir, start=file_handler.home_dir)
                return render_template('not_found.html', cache_dir=cache_dir, num=len(file_handler.cache_folders))

            print(Fore.YELLOW + f'当前文件夹中子文件夹的数量: <{len(file_handler.cache_folders)}>')
            # 获取当前文件夹在子文件夹列表中的位置
            current_folder_index = file_handler.cache_folders.index(relative_path)  # 查找relative_path 即image的父目录，在 cache_folders 中的索引

            # 获取上一个文件夹和下一个文件夹的路径
            prev_folder = file_handler.cache_folders[current_folder_index - 1] if current_folder_index > 0 else None
            next_folder = file_handler.cache_folders[current_folder_index + 1] if current_folder_index < len(file_handler.cache_folders) - 1 else None

            # 准备渲染导航HTML需要的内容
            if prev_folder:
                prev_display = 'flex'
                prev_path = quote(prev_folder)
                prev_name = os.path.basename(prev_folder)
            else:
                prev_display = 'none'
                prev_path = ''
                prev_name = ''
            if next_folder:
                next_display = 'flex'
                next_path = quote(next_folder)
                next_name = os.path.basename(next_folder)
            else:
                next_display = 'none'
                next_path = ''
                next_name = ''

            # 根据设备类型选择模板文件
            template_file = "gallery_mobile.html" if is_mobile_flag else "gallery_desktop.html"

            return render_template(template_file, title=folder_name, imgs_num=len(image_files), images=images_to_display,
                                                  prev_display=prev_display, prev_path=prev_path, prev_name=prev_name, next_display=next_display, next_path=next_path, next_name=next_name,
                                                  relative_path=relative_path, total_pages=total_pages, page=page)
    else:
        return "<h1>404 Directory not found.</h1>", 404

@app.route('/view_img')
def view_img():
    relative_path = request.args.get('path', '')

    # 安全检查
    full_path = safe_path_check(relative_path)

    if os.path.isfile(full_path) and is_img(full_path):
        img_ext = os.path.splitext(full_path)[1]
        img_ext = img_ext[1:]  # remove .
        img_ext = img_ext.lower()
        img_ext = 'jpeg' if img_ext == 'jpg' else img_ext
        mimetype = f'image/{img_ext}'
        return send_file(full_path, mimetype=mimetype)
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

    return render_template('search.html', title=f"搜索结果: {query}", query=query, results=search_results)

@app.route('/random_subdir')
def random_subdirectory():
    # 获取当前目录的子目录
    relative_path = request.args.get('path', '')

    # 安全检查
    full_path = safe_path_check(relative_path)

    print(Fore.YELLOW + f"当前目录: [{full_path}] 开始获取子目录...")

    if os.path.isdir(full_path):
        subdirectories = file_handler.get_subdirectories(full_path)
        print(Fore.GREEN + f"成功获取子目录 其长度为: <{len(subdirectories)}> 开始从中随机选择子目录...")
        if subdirectories:
            # 随机选择一个子目录
            random_dir = choice(subdirectories)
            print(Fore.GREEN + f"随机选中: [{random_dir}]")
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
        print(f"\nStop monitoring: [{home_dir}].")
    observer.join()
