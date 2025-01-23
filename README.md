# AlbumServer

## Python环境

Python 3.12

## 安装依赖

进入项目根目录，执行命令

```sh
$ pip install -r requirements.txt
```

## 运行Server

进入项目根目录

使用方式：

```sh
# Linux
$ chmod +x album_server.py
$ ./album_server.py[ --port PORT --home ALBUM_HOME_DIR --items items_per_index_page --imgs imgs_per_gallery_page]

# Windows
$ python album_server.py[ --port PORT --home ALBUM_HOME_DIR --items items_per_index_page --imgs imgs_per_gallery_page]
```

示例：

```bash
# Linux
$ ./album_server.py # 使用album_server.py中的PORT, HOME_DIR等默认值

# Windows
$ python album_server.py # 使用album_server.py中的PORT, HOME_DIR等默认值
```

