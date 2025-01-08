import os
import re
import socket
from urllib.parse import quote

# 初始化
ITEMS_PER_PAGE = 50
IMGS_PER_PAGE = 24
image_suffixes = ['.jpg', '.jpeg', '.webp', '.png', '.avif']

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
            # test
            print(f'Change last_folder_directory to {self.last_folder_directory}')
            self.last_subdirectories = self.subdirectories4home_dir
            # test
            print('Use subdirectories4home_dir')
            return self.subdirectories4home_dir
        if directory != self.last_folder_directory:
            subdirectories = [os.path.relpath(entry.path, start=self.home_dir) for entry in os.scandir(directory) if entry.is_dir()]
            subdirectories.sort(key=lambda x: list(map(ord, x)))
            if subdirectories:  # subdirectories非空 按照本应用的逻辑 应该进入这些子目录的index页
                self.last_folder_directory = directory
                # test
                print(f'Change last_folder_directory to {self.last_folder_directory}')
                self.last_subdirectories = subdirectories
            return subdirectories
        # test
        print('Use last_subdirectories')
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
        # test
        print('Use last_image_files')
        return self.last_image_files

    def search_folders(self, query, depth="shallow"):
        results = []
        if depth == "shallow":
            # test
            print(f"Shallow search in {self.current_dir}")
            # 仅搜索当前目录
            for item in os.listdir(self.current_dir):
                if query.lower() in item.lower() and os.path.isdir(os.path.join(self.current_dir, item)):
                    results.append(os.path.relpath(os.path.join(self.current_dir, item), start=self.home_dir))
        elif depth == "deep":
            # test
            print(f"Deep search in {self.current_dir}")
            # 深度搜索当前目录及其子目录
            for root, dirs, _ in os.walk(self.current_dir):
                for folder in dirs:
                    if query.lower() in folder.lower():
                        results.append(os.path.relpath(os.path.join(root, folder), start=self.home_dir))
        if len(results) > 1:
            self.last_folder_directory = f'<Search>: {query}'  # 伪路径 为了重复利用last_*的机制
            # test
            print(f'Change last_folder_directory to {self.last_folder_directory}')
            self.last_subdirectories = results
        return results
    
    def generate_gallery_html(self, image_paths, relative_parent_path, page=1, user_agent=''):
        # 获取当前文件夹的名称 relative_parent_path即images的父目录
        folder_name = os.path.basename(relative_parent_path)
        total_images = len(image_paths)
        total_pages = (total_images + IMGS_PER_PAGE - 1) // IMGS_PER_PAGE
        start_index = (page - 1) * IMGS_PER_PAGE
        end_index = start_index + IMGS_PER_PAGE
        images_to_display = image_paths[start_index:end_index]
        is_mobile_flag = is_mobile(user_agent)

        # 根据设备类型选择 img 标签
        if is_mobile_flag:
            images_html = "\n".join([
                f"<div class='item'><img class='lazy' src='/asset/placeholder.svg' data-original='/view_img?path={quote(image_path)}' alt='{folder_name}'></div>"
                for image_path in images_to_display
            ])
        else:
            images_html = "\n".join([
                f"<li class='thumb'> <img class='lazy' src='/asset/placeholder.svg' data-original='/view_img?path={quote(image_path)}' alt='{folder_name}'> </li>"
                for image_path in images_to_display
            ])

        # 确保 relative_parent_path 即image的父目录相对home_dir的相对路径在 last_subdirectories 中
        if relative_parent_path not in self.last_subdirectories:
            print(f"Warning: {relative_parent_path} not found in last_subdirectories.")
            return f"Error: Folder not found. Len of self.last_subdirectories is {len(self.last_subdirectories)}"

        # test:
        print(f'Current len of dirs: {len(self.last_subdirectories)}')
        
        # 获取当前文件夹在子文件夹列表中的位置
        current_folder_index = self.last_subdirectories.index(relative_parent_path)  # 查找relative_parent_path 即image的父目录，在 last_subdirectories 中的索引

        # 获取上一个套图和下一个套图的路径
        prev_folder = self.last_subdirectories[current_folder_index - 1] if current_folder_index > 0 else None
        next_folder = self.last_subdirectories[current_folder_index + 1] if current_folder_index < len(self.last_subdirectories) - 1 else None

        # 生成切换套图按钮
        nav_html = "<nav id='nav'>"
        if prev_folder:
            prev_path = quote(prev_folder)
            with open('template/nav-previous.html') as f:
                template = f.read()
            nav_html += template.format(prev_path, os.path.basename(prev_folder))
        # 填充一行
        nav_html += "</br>"
        if next_folder:
            next_path = quote(next_folder)
            with open('template/nav-next.html') as f:
                template = f.read()
            nav_html += template.format(next_path, os.path.basename(next_folder))
        nav_html += "</nav>"

        # 添加分页 HTML
        pagination_html = "<div class='pagination'>"
        if page > 1:
            pagination_html += f"<a class='prev' href='/view_dir?path={quote(relative_parent_path)}&page={page - 1}'>Last</a> "
        if total_pages > 1:
            for i in range(1, total_pages + 1):
                if i == page:
                    pagination_html += f"<a class='current' href='/view_dir?path={quote(relative_parent_path)}&page={i}'>{i}</a> "
                else:
                    pagination_html += f"<a href='/view_dir?path={quote(relative_parent_path)}&page={i}'>{i}</a> "
        if page < total_pages:
            pagination_html += f"<a class='next' href='/view_dir?path={quote(relative_parent_path)}&page={page + 1}'>Next</a>"
        pagination_html += "</div>"

        # 根据设备类型选择模板
        template_file = "template/gallery_mobile.html" if is_mobile_flag else "template/gallery_desktop.html"

        with open(template_file, encoding='UTF-8') as f:
            template = f.read()
        return template.format(folder_name, images_html, nav_html + pagination_html)

    def generate_index_html(self, folders, relative_parent_path, page=1, search_query=""):
        total_folders = len(folders)
        total_pages = (total_folders + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        start_index = (page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        folders_to_display = folders[start_index:end_index]

        folders_html = "\n".join([
            f"<li><a href='/view_dir?path={quote(folder)}'>{os.path.basename(folder)}</a></li>"
            for folder in folders_to_display
        ])
        pagination_html = ""
        if total_pages > 1:
            pagination_html = "<div class='pagination'>"
            for i in range(1, total_pages + 1):
                if i == page:
                    pagination_html += f"<a class='current' href='/view_dir?path={quote(relative_parent_path)}&page={i}'>{i}</a> "
                else:
                    pagination_html += f"<a href='/view_dir?path={quote(relative_parent_path)}&page={i}'>{i}</a> "
            pagination_html += "</div>"
        with open('template/index.html', encoding='UTF-8') as f:
            template = f.read()
        if relative_parent_path == '':
            relative_parent_path = '/'
        return template.format(f"当前目录: {relative_parent_path}", search_query, relative_parent_path, folders_html, pagination_html)

    def generate_search_html(self, search_results, search_query):
        search_results_html = "\n".join([
            f"<li><a href='/view_dir?path={quote(folder)}'>{os.path.basename(folder)}</a></li>"
            for folder in search_results
        ])
        with open('template/search.html', encoding='UTF-8') as f:
            template = f.read()
        return template.format(f"搜索结果: {search_query}", search_query, search_results_html)