import os
import re
from threading import Timer
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
def path_is_within(sub_path, parent_path):
    sub_path = os.path.abspath(sub_path)
    parent_path = os.path.abspath(parent_path)
    return sub_path == parent_path or sub_path.startswith(parent_path)

# 节流Throttling: 限制函数执行频率的技术
class Throttler:
    def __init__(self, interval, func):
        self.interval = interval
        self.func = func
        self.timer = None
    def call(self, *args, **kwargs):
        if self.timer:
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
            item_index = self.file_handler.cache_folders_for_home_dir
            item_index.remove(os.path.relpath(item, self.home_dir))
            print(Fore.YELLOW + f'Remove {item}')
        except ValueError as e:
            print(Fore.RED + str(e))
    def add_item(self, item):
        item_index = self.file_handler.cache_folders_for_home_dir
        item_index.append(os.path.relpath(item, self.home_dir))
        self.throttler.call(item_index)  # 使用节流器对item_index进行排序 防止频繁的排序导致阻塞
        print(Fore.GREEN + f'Add {item}')
    def on_created(self, event):
        print(f"Create: [{event.src_path}]")
        self.add_item(event.src_path)
    def on_deleted(self, event):
        print(f"Delete: [{event.src_path}]")
        self.remove_item(event.src_path)
    def on_moved(self, event):
        print(f"Move: [{event.src_path}] -> [{event.dest_path}]")
        self.remove_item(event.src_path)
        if path_is_within(event.dest_path, self.home_dir):
            self.add_item(event.dest_path)

# 文件工具类
class GalleryFileHandler():
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.current_dir = home_dir        # 实现在current_dir中搜索
        self.cache_folders_for_home_dir = self._get_folder_index(home_dir)  # 文件夹索引 仅包含文件夹
        self.cache_images_dir = ''         # 实现cache_images的复用
        self.cache_images = []
        self.cache_folders_dir = home_dir  # 实现cache_folders的复用 初始值为home_dir
        self.cache_folders = self.cache_folders_for_home_dir  # 两处使用cache_folders: 1.缓存,备用 2.生成前后切换图片文件夹的nav
    def _get_folder_index(self, dir):
        folder_index = []
        with os.scandir(dir) as entries:
            for entry in entries:
                if entry.is_dir():
                    folder_index.append(os.path.relpath(entry.path, self.home_dir))
        folder_index.sort(key=lambda x: list(map(ord, x)))
        return folder_index
    def get_subdir(self, directory):
        if directory.rstrip(os.sep) == self.cache_folders_dir.rstrip(os.sep):
            sub_dirs = self.cache_folders
            print(Fore.GREEN + f'命中文件夹列表缓存: [{self.cache_folders_dir}]')
        elif os.path.relpath(directory, self.home_dir) == '.':
            self.cache_folders_dir = self.home_dir
            print(Fore.YELLOW + f'更改文件夹缓存目录为: [{self.cache_folders_dir}]')
            sub_dirs = self.cache_folders_for_home_dir
        else:
            sub_dirs = self._get_folder_index(directory)
            if sub_dirs:  # sub_dirs非空 按照本应用的逻辑 应该进入展示这些子目录的index页 所以缓存目录更改
                self.cache_folders_dir = directory
                print(Fore.YELLOW + f'更改文件夹缓存目录为: [{self.cache_folders_dir}]')
                self.cache_folders = sub_dirs
        return sub_dirs
    def get_image_files(self, directory):
        if directory.rstrip(os.sep) != self.cache_images_dir.rstrip(os.sep):
            image_files = [
                os.path.relpath(entry.path, start=self.home_dir)
                for entry in os.scandir(directory) if is_img(entry.name)
            ]
            image_files.sort(key=extract_first_number)
            self.cache_images_dir = directory
            print(Fore.YELLOW + f'更改图片缓存目录为: [{self.cache_images_dir}]')
            self.cache_images = image_files
        else:
            image_files = self.cache_images
            print(Fore.GREEN + f'命中图片列表缓存: {self.cache_images_dir}')
        return image_files
    def search_folders(self, query):
        results = []
        print(Fore.CYAN + f"Search in [{self.current_dir}].")
        sub_dirs = self.get_subdir(self.current_dir)
        for sub_dir in sub_dirs:
            if query.lower() in sub_dir.lower():  # 大小写不敏感
                results.append(sub_dir)
        if len(results) > 1:
            self.cache_folders_dir = f'(Search): {query}'  # 伪路径 为了重复利用cache_*的机制
            print(Fore.YELLOW + f'更改文件夹缓存目录为: [{self.cache_folders_dir}]')
            self.cache_folders = results
        return results
