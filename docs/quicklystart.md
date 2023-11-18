# 快速开始
## 基础配置
首先，您需要设置一些基础配置以支持您的运行  
您需要设置**环境变量**来配置您的应用  

|      变量名      |     变量值      |      作用      | 是否必须 |
|:-------------:|:------------:|:------------:|:----:|
|  CUSTOM_PATH  |  详细路径(字符串)   |  自定义您的保存路径   |  是   |
| DEFAULT_DMODE | `txt`或`epub` | 自定义前端默认的下载模式 |  否   |

<br />

如果您需要开启web下载，那么您需要开启webdav模式。  
我们在此处推荐您使用[alist](https://github.com/alist-org/alist)作为您的webdav服务器  
开启后、您的`下载任务`内的按钮将会链接到正确的位置  
**提示：若果您不开启webdav模式，您`下载任务`内的按钮将不会正确链接，您将收到报错！**

|       变量名       |  变量值   |         作用         | 是否必须 |
|:---------------:|:------:|:------------------:|:----:|
|    IS_WEBDAV    | `True` |     开启webdav模式     |  否   |
|   WEBDAV_URL    |  字符串   |   设置webdav服务器的地址   |  否   |
| WEBDAV_USERNAME |  字符串   |  设置webdav服务器的用户名   |  否   |
|   WEBDAV_PWD    |  字符串   |   设置webdav服务器的密码   |  否   |
|   PUBLIC_URL    |  字符串   | 设置`下载任务`内`下载`按钮的地址 |  否   |

如何配置？例如，您的webdav服务器为 `http://example.org/` ，您下载了一个`a.txt`的文件，它将会自动上传到webdav服务器中的`/public`目录下， 也就是 `http://example.org/public` 目录，此时您可通过浏览器直接访问 `http://example.org/public/a.txt` 来下载您的文件。  

然后，您可以设置`PUBLIC_URL`为 `http://example.org/public` 来使`下载任务`内`下载`按钮的地址正确的链接，此时您在web页面点击`下载任务`内`下载`按钮的地址，它将会被链接到正确的地址(如`http://example.org/public/a.txt`)  

## 源码运行

在使用源码运行前，您需要先下载一个3.0以上的python，同时您需要保证此python解释器具有pip。  
您需要在运行前进行[设置](#基础配置)，完成后，您才可以使用源码正常地运行。

```shell
git clone https://github.com/weiwei-cool/FanQieNovelDownloadOnWeb.git
cd FanQieNovelDownloadOnWeb
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
## Docker运行
如果您需要使用docker运行请使用以下命令  
您可在容器的/app/logs内找到日志，您可自行添加映射  
**重要提示：如果您的服务部署在ipv6上，请一定开启Docker的ipv6模式，并启动您服务器的ipv6转发！**

以普通模式运行，此时您`下载任务`内`下载`按钮将无法点击，点击后会出现报错。  
您可直接在您环境变量中您自定义的路径找到下载的文件
```shell
docker run --name="fanqie"\
 -v {Lpath}:{path}\
 -e CUSTOM_PATH={path}\
 --restart=unless-stopped\
 -p 8000:8000\
 -d weiweicool/fanqie-novel-download-on-web
```
您需要替换`{path}`为您容器内的下载位置，设置`{Lpath}`为您本地映射的路径。  

同时，与源码运行一样，您也可以以webdav模式运行。
```shell
docker run --name="fanqie"\
 -v {Lpath}:{path}\
 -e CUSTOM_PATH={path}\
 -p 8000:8000\
 -e WEBDAV_USERNAME={user_name}\
 -e WEBDAV_PWD={pwd}\
 -e WEBDAV_URL={your_webdav_url}\
 -e PUBLIC_URL={your_public_url}\
 -e IS_WEBDAV=True\
 --restart=unless-stopped\
 -d weiweicool/fanqie-novel-download-on-web
```
您需要按照[设置](#基础配置)来依依配置您的环境变量。

## 大功告成
您现在即可在8000端口或您自定义的端口上查看您的程序了！