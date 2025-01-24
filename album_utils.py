import os
import re
from threading import Timer
from colorama import init, Fore
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        self.timers = {}  # 存储定时器的字典
    
    def call(self, *args, **kwargs):
        timer_id = id(args[0]) # 使用第一个参数的id作为唯一标识,实现当传入的第一个参数地址不同时,使用不同的timer
        # 如果存在对应id的活动的定时器，则取消它
        if timer_id in self.timers:
            self.timers[timer_id].cancel()
            print(Fore.YELLOW + f'Cancel timer {timer_id}')
        # 创建一个新的定时器，时间间隔走完后执行函数
        self.timers[timer_id] = Timer(self.interval, self.func, args=(*args, self.timers), kwargs=kwargs)
        self.timers[timer_id].start()
        print(Fore.GREEN + f'Create new timer {timer_id}')

# 自定义 observer，只监控目录
class DirectoryOnlyObserver(Observer):
    def _add_watch(self, path, *args, **kwargs):
        # 如果是文件，则跳过监控，防止在因为文件过多，导致OSError: [Errno 28] inotify watch limit reached
        if not os.path.isdir(path):
            return None
        super()._add_watch(path, *args, **kwargs)

# 监控文件更改
class DirectoryEventHandler(FileSystemEventHandler):
    def __init__(self, file_handler, throttler):
        super().__init__()
        self.file_handler = file_handler
        self.home_dir = self.file_handler.home_dir  # 不会更新 所以存储下来以便使用
        self.throttler = throttler
    def _get_index_of_item(self, item):
        try:
            item_rel_path = os.path.relpath(item, start=self.home_dir)
            item_index = self.file_handler.folder_index.get(item_rel_path.rsplit(os.sep, maxsplit=1)[0], [])
            return item_index
        except ValueError as e:
            print(str(e))
    def remove_item(self, item):
        try:
            item_index = self._get_index_of_item(item)
            item_index.remove(os.path.basename(item))
            print(Fore.YELLOW + f'Remove {item}')
        except ValueError as e:
            print(str(e))
    def add_item(self, item):
        item_index = self._get_index_of_item(item)
        item_index.append(os.path.basename(item))
        self.throttler.call(item_index)  # 使用节流器对item_index进行排序 防止频繁的排序导致阻塞
        print(Fore.GREEN + f'Add {item}')
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
        self.folder_index.get('', []).sort(key=lambda x: list(map(ord, x)))  # 排序home_dir中的子文件
        self.cache_folders_for_home_dir = self.folder_index.get('', [])  # 因为此处传递的是地址 因此watchdog修改cache_folders_for_home_dir就是修改folder_index
        self.cache_folders = self.cache_folders_for_home_dir  # 两处使用cache_folders: 1.缓存,备用 2.生成前后切换图片文件夹的nav
    def _get_rel_path_to_home(self, abs_path):
        rel_path = os.path.relpath(abs_path, start=self.home_dir)
        if rel_path == '.':
            rel_path = ''
        return rel_path
    def _build_folder_index(self, root_dir):
        """
        构造文件夹索引，只记录所有文件夹路径。
        :param root_dir: 根目录路径
        :return: 文件夹索引（字典）
        """
        folder_index = {}
        def scan_directory(current_dir):
            # 获取当前文件夹的相对路径作为 key
            rel_path = self._get_rel_path_to_home(current_dir)
            # 初始化当前文件夹的子文件夹列表
            folder_index[rel_path] = []
            subdirs = []
            # 遍历当前目录中的条目
            with os.scandir(current_dir) as entries:
                for entry in entries:
                    if entry.is_file() and current_dir != self.home_dir:  # home_dir 除外
                        break  # 如果存在文件，跳过该文件夹的进一步扫描 某些时候可能导致文件夹扫描不完全
                    if entry.is_dir():
                        folder_index[rel_path].append(entry.name)
                        subdirs.append(entry.path)
            return subdirs
        # 使用线程池并行扫描
        with ThreadPoolExecutor() as executor:
            tasks = [ root_dir ]  # 初始化任务队列
            while tasks:
                futures = {executor.submit(scan_directory, task): task for task in tasks}
                tasks = []
                for future in as_completed(futures):
                    tasks.extend(future.result())  # 将新发现的子目录加入任务队列
        return folder_index
    def get_subdirectories(self, directory):
        rel_path = self._get_rel_path_to_home(directory)
        if directory.rstrip(os.sep) != self.cache_folders_dir.rstrip(os.sep):
            sub_foldernames = self.folder_index.get(rel_path, [])
            sub_foldernames.sort(key=lambda x: list(map(ord, x)))  # LazySort,只有使用时才sort
            if rel_path != '':
                sub_folders = [os.path.join(rel_path, sub_foldername) for sub_foldername in sub_foldernames]
            else:
                sub_folders = sub_foldernames
            if sub_folders:  # sub_folders非空 按照本应用的逻辑 应该进入展示这些子目录的index页 所以缓存目录更改
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
                os.path.relpath(entry.path, start=self.home_dir)
                for entry in os.scandir(directory) if is_img(entry.name)
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
        rel_path = self._get_rel_path_to_home(self.current_dir)
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
