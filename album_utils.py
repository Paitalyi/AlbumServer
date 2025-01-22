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
            self.file_handler.subdirectories4home_dir.remove(os.path.relpath(item, start=self.home_dir))
            print(Fore.GREEN + 'Remove ', item)
        except ValueError as e:
            print(str(e))
    def add_item(self, item):
        self.file_handler.subdirectories4home_dir.append(os.path.relpath(item, start=self.home_dir))
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
        self.current_dir = home_dir  # 实现在current_dir中搜索
        self.last_image_directory = ''  # 实现last_image_files的复用
        self.last_image_files = []
        self.last_folder_directory = home_dir  # 实现last_subdirectories的复用
        self.subdirectories4home_dir = self._get_initial_subdirectories(home_dir)
        self.last_subdirectories = self.subdirectories4home_dir

    def _get_initial_subdirectories(self, directory):
        subdirectories = [os.path.relpath(entry.path, start=self.home_dir) for entry in os.scandir(directory) if entry.is_dir()]
        subdirectories.sort(key=lambda x: list(map(ord, x)))
        return subdirectories

    def get_subdirectories(self, directory):
        if directory in [self.home_dir, f'{self.home_dir}\\', f'{self.home_dir}/']:
            self.last_folder_directory = directory
            print(Fore.YELLOW + f'切换缓存文件夹目录为: [{self.last_folder_directory}].')
            self.last_subdirectories = self.subdirectories4home_dir
            print(Fore.GREEN + '使用缓存: subdirectories4home_dir')
            return self.subdirectories4home_dir
        if directory != self.last_folder_directory:
            subdirectories = [os.path.relpath(entry.path, start=self.home_dir) for entry in os.scandir(directory) if entry.is_dir()]
            subdirectories.sort(key=lambda x: list(map(ord, x)))
            if subdirectories:  # subdirectories非空 按照本应用的逻辑 应该进入这些子目录的index页
                self.last_folder_directory = directory
                print(Fore.YELLOW + f'切换缓存文件夹路径为: [{self.last_folder_directory}].')
                self.last_subdirectories = subdirectories
            return subdirectories
        print(Fore.GREEN + '使用缓存: last_subdirectories')
        return self.last_subdirectories

    def get_image_files(self, directory):
        if directory != self.last_image_directory:
            image_files = [
                os.path.relpath(os.path.join(directory, file), start=self.home_dir)
                for file in os.listdir(directory) if is_img(file)
            ]
            image_files.sort(key=extract_first_number)
            self.last_image_directory = directory
            self.last_image_files = image_files
            return image_files
        print(Fore.GREEN + '使用缓存: last_image_files')
        return self.last_image_files

    def search_folders(self, query, depth="shallow"):
        results = []
        if depth == "shallow":
            print(Fore.CYAN + f"Shallow search in [{self.current_dir}].")
            # 仅搜索当前目录
            for item in os.listdir(self.current_dir):
                if query.lower() in item.lower() and os.path.isdir(os.path.join(self.current_dir, item)):
                    results.append(os.path.relpath(os.path.join(self.current_dir, item), start=self.home_dir))
        elif depth == "deep":
            print(Fore.CYAN + f"Deep search in [{self.current_dir}].")
            # 深度搜索当前目录及其子目录
            for root, dirs, _ in os.walk(self.current_dir):
                for folder in dirs:
                    if query.lower() in folder.lower():
                        results.append(os.path.relpath(os.path.join(root, folder), start=self.home_dir))
        if len(results) > 1:
            self.last_folder_directory = f'(Search): {query}'  # 伪路径 为了重复利用last_* 实现不同图片文件夹的切换
            print(Fore.YELLOW + f'切换缓存文件夹路径为: [{self.last_folder_directory}].')
            self.last_subdirectories = results
        return results