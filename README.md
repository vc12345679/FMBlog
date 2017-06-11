# 关于FMBlog

[FMBlog](https://github.com/vc12345679/FMBlog) = F(lask) + M(istune) + Blog

顾名思义，FMBlog 是一个基于 [flask](https://github.com/pallets/flask)，
并使用 [mistune](https://github.com/lepture/mistune) 进行 Markdown解析
的博客系统。

FMBlog 当前版本 v0.1 alpha，仍在开发中。

FMBlog 以 [BSD 3-Clause 许可证](https://github.com/vc12345679/FMBlog/blob/master/LICENSE)
发布。

# FMBlog 的使用

## 初始化

### 拷贝文件

```
git clone https://github.com/vc12345679/FMBlog.git ./
```

或 点击下载 [最新文件.zip](https://github.com/vc12345679/FMBlog/archive/master.zip)

请确保 blogs 文件夹 和 app/static 文件夹 的权限，使得运行 FMBlog 和 
相应web服务 的用户能够读取文件（需要文件夹的 读取权限、执行权限 和文件夹内文件的 读取权限）。

### 建立 sqlite 数据库

在 FMBog 文件夹下运行

```python
python3 manage.py shell
from app import db
db.create_all()
```

因为当前还处于 alpha 版，所以默认运行配置为 Development；
如需 Production/Testing 环境，请自行在 config.py 中调整。
相关设置今后会在配置文件中留出配置项。TODO

### 建立配置文件

```
cp user_config.py.example user_config.py
```

当前配置文件还略显混乱，后续会进行优化。TODO

## 运行 FMBlog

作者是采用 nginx + uWSGI emperor 的模式来运行 FMBlog 的，这里只给出相应的配置示例。
其它类型请大家自行探索/搜索，作者也是小白啊……

作者的 FMBlog 路径为 `/home/http/www/FMBlog`，nginx 以 www-data:www-data 用户身份运行。

### uWSGI emperor

非 pip方式 安装的用户，请确认在安装 uWSGI 的时候，同时安装了 uWSGI 的 python 插件。

作者的 uWSGI 以 systemd 服务方式运行，deb一系和其它系列发行版可能在用包管理器
安装 uWSGI 时已默认添加，作者是用的 archlinux，pip 安装的 uwsgi，
这里给出一个 emperor.uwsgi.service 配置文件示例。

```ini
[Unit]
Description=uWSGI Emperor
After=syslog.target

[Service]
ExecStart=/usr/local/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -INI $MAINPID
Restart=always
Type=notify
StandardError=syslog
NotifyAccess=all
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
```

可以发现 uwsgi 的配置指向 `/etc/uwsgi/uwsgi.ini`，相应配置文件的内容为

```ini
[uwsgi]
uid = www-data
gid = www-data
chdir = /home/http/FMBlog/
processes = 4
threads = 2

wsgi-file = manage.py
callable = app

socket = /tmp/fmblog.sock
chmod-socket = 666
chown-socket = www-data:www-data

logto = /var/log/uwsgi/fmblog.log
```

uWSGI 以 www-data:www-data 用户身份运行；
socket 文件为`/tmp/fmblog.sock`；
日志文件为`/var/log/uwsgi/fmblog.log`。

这只是一种偷懒的配置方式，大家可自行调整为多文件配置模式或多配置块模式。

### nginx

```
location / {
    include uwsgi_params;
    if (!-f $request_filename) {
        uwsgi_pass unix:///tmp/fmblog.sock;
    }
}

location /static/ {
        alias /home/http/FMBlog/app/static/;
}
```

这里只给出 nginx 配置文 location 级的块配置，其它个性功能请自行添加。

第一个 `/` 块中，uwsgi 要指向上一步 uwsgi.ini 中配置的 socket 文件；

第二个 `/static/` 块是为了让 nginx 接管 flask 静态文件，毕竟效率要高不少。

## 撰写博客

### 文件名

博客文件的文件名必须以 `.md` 为扩展名

### 权限

需要运行web服务和flask程序的用户能够读取。

### 博客信息

博客文件需要包含一段配置信息，这段信息是被包含在HTML的块注释符`<!-- ... -->`内的，
配置信息位置建议放在文件头部。

配置内容实际上为 yaml 格式，必须的字段为

|字段|说明|
|:-:|:-:|
|author|作者|
|date| 日期，形式如 2017-06-10|
|title| 博客标题，中英文均可|
|tag| 标签列表，包含在[...]内，大小写不敏感，中英文均可|
|category| 所属分类列表，包含在[...]内，大小写敏感，中英文均可|
|summary| 博客概述/摘要，中英文均可，如需换行请遵循YAML格式|

例如

```
<!--
author: vc12345679
date: 2017-06-10
title: FMBlog README
tag: [fmblog]
category: [FMBlog, Technology]
summary: Introduction of FMBlog
-->
```

### 博客内容

博客文件的其它部分即为 Markdown 博客内容

# FMBlog 后续开发计划

* doc 完善文档

* user_config 优化配置文件

* unittest 添加单元测试

* i18n 多语言界面

* cache 模板/页面缓存

* 优化更新策略

* 提供通用接口