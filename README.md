# AlbumServer

## Python环境

Python 3.12

## 安装依赖

进入项目根目录：

```sh
$ pip install -r requirements.txt
```

## 运行Server

进入项目根目录：

```sh
# 命令格式
$ python album_server.py [PORT] [ALBUM_HOME_DIR]

# e.g.
$ python album_server.py
# 默认使用album_server.py中的PORT, HOME_DIR

$ python album_server.py 80 /mnt/media
# 使用80端口(HTTP默认), 展示/mnt/media目录下面的相册(文件夹)

$ python album_server.py 80 "D:\图片"
# 使用80端口(HTTP默认), 展示"D:\图片"目录下面的相册(文件夹)
```

