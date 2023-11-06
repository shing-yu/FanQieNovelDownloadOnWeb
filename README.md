# FanQieNovelDownloadOnWeb
一个用以下载番茄小说的web应用

## 特点

 - 优秀的django python网络服务应用
 - 快速的docker部署
 - 支持amd和arm两种架构
 - 支持txt、epub格式保存

## 使用方法
### 源码运行
```shell
git clone https://github.com/weiwei-cool/FanQieNovelDownloadOnWeb.git
cd FanQieNovelDownloadOnWeb
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
### docker运行
如果您需要使用docker运行请使用以下命令
```shell
docker run --name="fanqie"\
 -v /root/alist/book/books:/root/alist/book/books\
 --restart=unless-stopped\
 -p 8000:8000\
 -d weiweicool/fanqie-novel-download-on-web
``` 

如果您**想要**开启**WebDav**模式，请设置环境变量`IS_WEBDAV=True`  
以**WebDav**模式运行时，应用会将下载完成的小说自动上传至webdav服务器中的/public目录下  
请将`{user_name}`和`{pwd}`替换为您的webdav账号密码  
**注意！如果您的webdav服务器为纯ipv6访问，请您一定要将docker设置为允许ipv6(默认不支持)**
```shell
docker run --name="fanqie"\
 -v /root/alist/book/books:/root/alist/book/books\
 -p 8000:8000\
 -e WEBDAV_USERNAME={user_name}\
 -e WEBDAV_PWD={pwd}\
 -e IS_WEBDAV=True\
 --restart=unless-stopped\
 -d weiweicool/fanqie-novel-download-on-web
```


## 开源与许可证
此项目使用来自 @xing-yv的[fanqie-novel-download](https://github.com/xing-yv/fanqie-novel-download)的源代码  
依据 GPLv3.0 第5条c) ，本项目使用 GPLv3.0 协议开源。
您可以在[此处](https://www.gnu.org/licenses/gpl-3.0.html)找到许可证的副本， 

## 免责声明
此程序旨在用于与Python网络爬虫和网页处理技术相关的教育和研究目的。不应将其用于任何非法活动或侵犯他人权利的行为。用户对使用此程序引发的任何法律责任和风险负有责任，作者和项目贡献者不对因使用程序而导致的任何损失或损害承担责任。

在使用此程序之前，请确保遵守相关法律法规以及网站的使用政策，并在有任何疑问或担忧时咨询法律顾问。

您因使用此软件产生的一切法律纠纷与开发者无关

## 作者
 
 - 思维（weiweicool）[github](https://github.com/weiwei-cool)

## 反馈

如果您遇到问题或有改进建议，请将其提交到此项目的[GitHub issues](https://github.com/weiwei-cool/FanQieNovelDownloadOnWeb/issues)页面。
