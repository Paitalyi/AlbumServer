import os
import re
import socket
from threading import Timer
from urllib.parse import quote
from colorama import init, Fore
from watchdog.events import FileSystemEventHandler

# 初始化colorama
init(autoreset=True)

# 初始化
image_suffixes = ['.jpg', '.jpeg', '.webp', '.png', '.avif', '.gif']

# 工具函数
def is_img(img_path):
    img_name = os.path.basename(img_path)
    return any(suffix in img_name.lower() for suffix in image_suffixes)
def is_mobile(user_agent):
    mobile_agents = [
        "Android", "iPhone", "iPad", "iPod", "BlackBerry", "Opera Mini", "IEMobile"
    ]
    return any(agent in user_agent for agent in mobile_agents)
def extract_first_number(file_path):
    basename = os.path.basename(file_path)
    match = re.search(r'(\d+)', basename)
    return int(match.group(1)) if match else float('inf')

# 节流Throttling: 限制函数执行频率的技术
class Throttler:
    def __init__(self, interval, func):
        self.interval = interval
        self.func = func
        self.timer = None
    def call(self, *args, **kwargs):
        # 如果存在活动的定时器，则取消它
        if self.timer is not None:
            self.timer.cancel()
        # 创建一个新的定时器，时间间隔走完后执行函数
        self.timer = Timer(self.interval, self.func, args=args, kwargs=kwargs)
        self.timer.start()

# 监控文件更改
class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, file_handler, throttler):
        super().__init__()
        self.file_handler = file_handler
        self.home_dir = self.file_handler.home_dir  # 不会更新 所以存储下来以便使用
        self.throttler = throttler
    def remove_item(self, item):
        try:
            self.file_handler.cache_folders_for_home_dir.remove(os.path.relpath(item, start=self.home_dir))
            print(Fore.GREEN + 'Remove ', item)
        except ValueError as e:
            print(str(e))
    def add_item(self, item):
        self.file_handler.cache_folders_for_home_dir.append(os.path.relpath(item, start=self.home_dir))
        self.throttler.call(self.file_handler)  # 使用节流器进行home_dir的subdir的排序
        print(Fore.GREEN + 'Add ' + item)
    def on_created(self, event):
        print(f"Create: [{event.src_path}], type: {'directory' if event.is_directory else 'file'}")
        if event.is_directory:
            self.add_item(event.src_path)
    def on_deleted(self, event):
        print(f"Delete: [{event.src_path}], type: {'directory' if event.is_directory else 'file'}")
        # if event.is_directory: # 某些watchdog版本 在删除事件后, event.is_directory会出错
        self.remove_item(event.src_path)
    def on_moved(self, event):
        print(f"Move: [{event.src_path}] -> [{event.dest_path}], type: {'directory' if event.is_directory else 'file'}")
        if event.is_directory:
            self.remove_item(event.src_path)
            self.add_item(event.dest_path)

# 文件工具类
class GalleryFileHandler():
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.current_dir = home_dir        # 实现在current_dir中搜索
        self.folder_index = self._build_folder_index(home_dir)  # 文件夹索引 仅包含文件夹
        self.cache_images_dir = ''         # 实现cache_images的复用
        self.cache_images = []
        self.cache_folders_dir = home_dir  # 实现cache_folders的复用
        self.cache_folders_for_home_dir = self.folder_index.get('', []).sort(key=lambda x: list(map(ord, x)))  # 因为此处传递的是地址 因此watchdog修改cache_folders_for_home_dir就是修改folder_index
        self.cache_folders = self.cache_folders_for_home_dir  # 两处使用: 1.缓存,备用 2.生成前后切换图片文件夹的nav
    def _build_folder_index(self, root_dir):
        """
        构造文件夹索引，只记录所有文件夹路径。
        :param root_dir: 根目录路径
        :return: 文件夹索引（字典）
        """
        folder_index = {}
        def scan_directory(current_dir):
            # 获取当前文件夹的相对路径作为 key
            relative_path = os.path.relpath(current_dir, root_dir)
            if relative_path == ".":
                relative_path = ""  # 根目录的相对路径设为空字符串
            # 初始化当前文件夹的子文件夹列表
            folder_index[relative_path] = []
            # 遍历当前目录中的条目
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if entry.is_file() and current_dir != self.home_dir:  # home_dir除外 但不是必须的
                        break  # 为了加速初始化 如果某个文件夹中如果存在文件 则默认其中没有文件夹 直接跳过
                        # 会导致: 同时存在文件夹和图片的文件夹 其中的子文件夹在目录树folder_index中很可能缺失
                    if entry.is_dir():
                        folder_index[relative_path].append(entry.name)
                        scan_directory(entry.path)
        scan_directory(root_dir)
        return folder_index
    def get_subdirectories(self, directory):
        rel_path = os.path.relpath(directory, self.home_dir)
        if rel_path == '.':
            rel_path = ''
        if directory.rstrip(os.sep) != self.cache_folders_dir.rstrip(os.sep):
            sub_foldernames = self.folder_index.get(rel_path, [])
            sub_foldernames.sort(key=lambda x: list(map(ord, x)))  # LazySort,只有使用时才sort
            if rel_path != '':
                sub_folders = [os.path.join(rel_path, sub_foldername) for sub_foldername in sub_foldernames]
            else:
                sub_folders = sub_foldernames
            if sub_folders:  # sub_folders非空 按照本应用的逻辑 应该进入这些子目录的index页 所以缓存目录更改
                self.cache_folders_dir = directory
                print(Fore.YELLOW + f'更改文件夹缓存目录为: [{self.cache_folders_dir}]')
                self.cache_folders = sub_folders
        else:
            sub_folders = self.cache_folders
            print(Fore.GREEN + f'命中文件夹列表缓存: [{self.cache_folders_dir}]')
        return sub_folders
    def get_image_files(self, directory):
        if directory.rstrip(os.sep) != self.cache_images_dir.rstrip(os.sep):
            image_files = [
                os.path.relpath(os.path.join(directory, file), start=self.home_dir)
                for file in os.listdir(directory) if is_img(file)
            ]
            image_files.sort(key=extract_first_number)
            self.cache_images_dir = directory
            print(Fore.YELLOW + f'更改图片缓存目录为: [{self.cache_images_dir}]')
            self.cache_images = image_files
            return image_files
        print(Fore.GREEN + f'命中图片列表缓存: {self.cache_images_dir}')
        return self.cache_images
    def search_folders(self, query, depth="shallow"):
        results = []
        def shallow_search(rel_path):
            sub_dirs = self.folder_index.get(rel_path, [])
            for sub_dir in sub_dirs:
                if query.lower() in sub_dir.lower():  # 大小写不敏感
                    results.append(os.path.join(rel_path, sub_dir))
        rel_path = os.path.relpath(self.current_dir, self.home_dir)
        if rel_path == '.':
            rel_path = ''
        if depth == "shallow":
            print(Fore.CYAN + f"Shallow search in [{self.current_dir}].")
            # 仅搜索当前目录
            shallow_search(rel_path)
        elif depth == "deep":
            print(Fore.CYAN + f"Deep search in [{self.current_dir}].")
            # 深度搜索当前目录及其子目录
            for key in self.folder_index.keys():
                if key.startswith(rel_path):
                    shallow_search(key)
        if len(results) > 1:
            self.cache_folders_dir = f'(Search): {query}'  # 伪路径 为了重复利用cache_*的机制
            print(Fore.YELLOW + f'更改文件夹缓存目录为: [{self.cache_folders_dir}]')
            self.cache_folders = results
        return results
