import re
import os
import json
import time
from urllib.parse import urljoin
from webdav4.client import Client
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import threading
from .models import History
from pathlib import Path


class Fanqie:
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 "
          "Safari/537.36 Edg/119.0.0.0")
    headers = {
        "User-Agent": ua
    }

    def __init__(self, url, mode):
        response = requests.get(url, headers=self.headers)
        self.url = url
        self.mode = mode
        self.html = response.text
        self.book_id = re.search(r"/(\d+)", url).group(1)

        self.obid = f'{self.book_id}-{self.mode}'

        self.soup = BeautifulSoup(self.html, "html.parser")

        self.title = self.soup.find("h1").get_text()
        self.title = rename(self.title)

        # 获取小说简介
        self.intro = self.soup.find("div", class_="page-abstract-content").get_text()

        # 获取小说作者
        self.author_name = self.soup.find('span', class_='author-name-text').get_text()

        # 找到type="application/ld+json"的<script>标签
        script_tag = self.soup.find('script', type='application/ld+json')

        # 提取每个<script>标签中的JSON数据
        json_data = json.loads(script_tag.string)
        images_data = json_data.get('image', [])
        # 打印提取出的images数据
        self.img_url = images_data[0]

    def __str__(self):
        return (f'FanqieNovel: {self.title}\n'
                f'author: {self.author_name}')


def rename(name):
    # 定义非法字符的正则表达式模式
    illegal_characters_pattern = r'[\/:*?"<>|]'

    # 定义替换的中文符号
    replacement_dict = {
        '/': '／',
        ':': '：',
        '*': '＊',
        '?': '？',
        '"': '“',
        '<': '＜',
        '>': '＞',
        '|': '｜'
    }

    # 使用正则表达式替换非法字符
    sanitized_path = re.sub(illegal_characters_pattern, lambda x: replacement_dict[x.group(0)], name)

    return sanitized_path


class DownloadNovel(threading.Thread):
    def __init__(self, fanqie: Fanqie):
        self.fanqie = fanqie
        self._stop_flag = False
        self._stop_event = threading.Event()
        self.is_webdav = os.environ.get('IS_WEBDAV')
        if self.is_webdav:
            self.webdav_username = os.environ.get('WEBDAV_USERNAME')
            self.webdav_pwd = os.environ.get('WEBDAV_PWD')
            self.webdav_url = os.environ.get('WEBDAV_URL')
            self.webdav = Client(base_url=self.webdav_url,
                                 auth=(self.webdav_username, self.webdav_pwd))
            print('webdav加载成功')
        super().__init__()

    def run(self) -> None:
        history_entry = History.objects.get(obid=self.fanqie.obid)
        print(self.fanqie)
        if self.fanqie.mode == 'txt':
            print('txt模式')

            content = f"""{self.fanqie.title}
            {self.fanqie.intro}
            """
            # 获取所有章节链接
            start_index = 0

            file_name = self.fanqie.title + ".txt"
            file_path = os.path.join('/root/alist/book/books', file_name)

            # 获取章节数
            chapters = self.fanqie.soup.find_all("div", class_="chapter-item")
            chapter_num = len(chapters)
            chapter_num_now = 0

            try:
                # 遍历每个章节链接
                for chapter in chapters[start_index:]:
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.25)
                    if self._stop_event.is_set():
                        break
                    # 获取章节标题
                    chapter_title = chapter.find("a").get_text()

                    # 获取章节网址
                    chapter_url = urljoin(self.fanqie.url, chapter.find("a")["href"])

                    # 获取章节 id
                    chapter_id = re.search(r"/(\d+)", chapter_url).group(1)

                    # 构造 api 网址
                    api_url = (f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&"
                               f"parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id="
                               f"{chapter_id}&item_id={chapter_id}")

                    # 尝试获取章节内容
                    chapter_content = None
                    retry_count = 1
                    while retry_count < 4:  # 设置最大重试次数
                        if self._stop_event.is_set():
                            break

                        def get_api():
                            # 获取 api 响应
                            api_response_ = requests.get(api_url, headers=self.fanqie.headers)

                            # 解析 api 响应为 json 数据
                            api_data_ = api_response_.json()
                            return api_data_

                        api_data = None
                        retry_get_api = 1
                        while retry_get_api < 4:
                            try:
                                api_data = get_api()
                            except Exception as e:
                                print(f"error:{e}")
                            else:
                                break
                            retry_get_api += 1

                        if "data" in api_data and "content" in api_data["data"]:
                            chapter_content = api_data["data"]["content"]
                            break  # 如果成功获取章节内容，跳出重试循环
                        else:
                            if retry_count == 1:
                                print(f"{chapter_title} 获取失败，正在尝试重试...")
                            print(f"第 ({retry_count}/3) 次重试获取章节内容")
                            retry_count += 1  # 否则重试

                    if retry_count == 4:
                        print(f"无法获取章节内容: {chapter_title}，跳过。")
                        continue  # 重试次数过多后，跳过当前章节

                    # 提取文章标签中的文本
                    chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)

                    # 将 <p> 标签替换为换行符
                    chapter_text = re.sub(r"<p>", "\n", chapter_text)

                    # 去除其他 html 标签
                    chapter_text = re.sub(r"</?\w+>", "", chapter_text)

                    chapter_text = fix_publisher(chapter_text)

                    # 在小说内容字符串中添加章节标题和内容
                    content += f"\n\n\n{chapter_title}\n{chapter_text}"

                    # 打印进度信息
                    print(f"已获取 {chapter_title}")
                    chapter_num_now += 1
                    history_entry.percent = round(
                        (chapter_num_now / chapter_num) * 100, 2)
                    history_entry.save()
                    print(f'进度：{history_entry.percent}%')
                # 根据编码转换小说内容字符串为二进制数据
                data = content.encode('utf-8', errors='ignore')

                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(data)

                file_path = os.path.join('/root/alist/book/books', file_name)
                file_path = Path(file_path)
                if self.is_webdav:
                    self.webdav.upload_file(from_path=file_path,
                                            to_path=os.path.join('/public', file_name),
                                            overwrite=True)
                    print("webdav保存成功")

                # 打印完成信息
                print(f"已保存{self.fanqie.title}.txt")

            except BaseException as e:
                # 捕获所有异常，及时保存文件
                print(f"发生异常: \n{e}")
                print("正在尝试保存文件...")
                # 根据编码转换小说内容字符串为二进制数据
                data = content.encode('utf-8', errors='ignore')

                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(data)

                print("文件已保存！")
                return

        elif self.fanqie.mode == 'epub':
            print('epub模式')

            # 创建epub电子书
            book = epub.EpubBook()

            # 下载封面
            response = requests.get(self.fanqie.img_url)
            # 获取图像的内容
            img_data = response.content

            # 保存图像到本地文件
            with open("cover.jpg", "wb") as f:
                f.write(img_data)

            # 创建一个封面图片
            book.set_cover("image.jpg", open('cover.jpg', 'rb').read())

            # 删除封面
            os.remove('cover.jpg')

            # 设置书的元数据
            book.set_title(self.fanqie.title)
            book.set_language('zh-CN')
            book.add_author(self.fanqie.author_name)
            book.add_metadata('DC', 'description', self.fanqie.intro)

            # 获取卷标
            page_directory_content = self.fanqie.soup.find('div', class_='page-directory-content')
            nested_divs = page_directory_content.find_all('div', recursive=False)

            # intro chapter
            intro_e = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='hr')
            intro_e.content = (f'<html><head></head><body>'
                               f'<img src="image.jpg" alt="Cover Image"/>'
                               f'<h1>{self.fanqie.title}</h1>'
                               f'<p>{self.fanqie.intro}</p>'
                               f'</body></html>')
            book.add_item(intro_e)

            # 创建索引
            book.toc = (epub.Link('intro.xhtml', '简介', 'intro'),)
            book.spine = ['nav', intro_e]

            # 获取章节数
            chapters = self.fanqie.soup.find_all("div", class_="chapter-item")
            chapter_num = len(chapters)
            chapter_num_now = 0

            try:
                volume_id = 0

                # 遍历每个卷
                for div in nested_divs:
                    if self._stop_event.is_set():
                        break
                    first_chapter = None
                    volume_id += 1
                    volume_div = div.find('div', class_='volume')
                    # 提取 "卷名" 文本
                    volume_title = volume_div.text
                    print(volume_title)
                    chapters = div.find_all("div", class_="chapter-item")
                    start_index = None
                    for i, chapter in enumerate(chapters):
                        if self._stop_event.is_set():
                            break
                        chapter_url_tmp = urljoin(self.fanqie.url, chapter.find("a")["href"])
                        chapter_id_tmp = re.search(r"/(\d+)", chapter_url_tmp).group(1)
                        if chapter_id_tmp == '0':  # epub模式不支持起始章节
                            start_index = i

                    # 定义目录索引
                    toc_index = ()

                    chapter_id_name = 0

                    # 遍历每个章节链接
                    for chapter in chapters[start_index:]:
                        chapter_id_name += 1
                        if self._stop_event.is_set():
                            break
                        time.sleep(0.25)
                        if self._stop_event.is_set():
                            break
                        # 获取章节标题
                        chapter_title = chapter.find("a").get_text()

                        # 获取章节网址
                        chapter_url = urljoin(self.fanqie.url, chapter.find("a")["href"])

                        # 获取章节 id
                        chapter_id = re.search(r"/(\d+)", chapter_url).group(1)

                        # 构造 api 网址
                        api_url = (f"https://novel.snssdk.com/api/novel/book/reader/full/v1/?device_platform=android&"
                                   f"parent_enterfrom=novel_channel_search.tab.&aid=2329&platform_id=1&group_id="
                                   f"{chapter_id}&item_id={chapter_id}")

                        # 尝试获取章节内容
                        chapter_content = None
                        retry_count = 1
                        while retry_count < 4:  # 设置最大重试次数
                            if self._stop_event.is_set():
                                break

                            def get_api():
                                # 获取 api 响应
                                api_response_ = requests.get(api_url, headers=self.fanqie.headers)

                                # 解析 api 响应为 json 数据
                                api_data_ = api_response_.json()
                                return api_data_

                            api_data = None
                            retry_get_api = 1
                            while retry_get_api < 4:
                                try:
                                    api_data = get_api()
                                except Exception as e:
                                    print(f"error:{e}")
                                else:
                                    break
                                retry_get_api += 1

                            if "data" in api_data and "content" in api_data["data"]:
                                chapter_content = api_data["data"]["content"]
                                break  # 如果成功获取章节内容，跳出重试循环
                            else:
                                if retry_count == 1:
                                    print(f"{chapter_title} 获取失败，正在尝试重试...")
                                print(f"第 ({retry_count}/3) 次重试获取章节内容")
                                retry_count += 1  # 否则重试

                        if retry_count == 4:
                            print(f"无法获取章节内容: {chapter_title}，跳过。")
                            continue  # 重试次数过多后，跳过当前章节

                        # 提取文章标签中的文本
                        chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)

                        # 在小说内容字符串中添加章节标题和内容
                        text = epub.EpubHtml(title=chapter_title,
                                             file_name=f'chapter_{volume_id}_{chapter_id_name}.xhtml')
                        text.content = chapter_text

                        toc_index = toc_index + (text,)
                        book.spine.append(text)

                        # 寻找第一章
                        if chapter_id_name == 1:
                            first_chapter = f'chapter_{volume_id}_{chapter_id_name}.xhtml'

                        # 加入epub
                        book.add_item(text)

                        # 打印进度信息
                        print(f"已获取 {chapter_title}")
                        chapter_num_now += 1
                        history_entry.percent = round(
                            (chapter_num_now / chapter_num) * 100, 2)
                        history_entry.save()
                        print(f'进度：{history_entry.percent}%')
                    # 加入书籍索引
                    book.toc = book.toc + ((epub.Section(volume_title, href=first_chapter),
                                            toc_index,),)
            except BaseException as e:
                # 捕获所有异常
                print(f"发生异常: \n{e}")
                return

            # 添加 navigation 文件
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            file_name = self.fanqie.title + ".epub"
            file_path = os.path.join('/root/alist/book/books', file_name)

            epub.write_epub(file_path, book, {})
            file_path = Path(file_path)
            if self.is_webdav:
                self.webdav.upload_file(from_path=file_path,
                                        to_path=os.path.join('/public', file_name),
                                        overwrite=True)
                print("webdav保存成功")

            print("文件已保存！")

    def stop(self):
        self._stop_event.set()


def fix_publisher(text):
    # 针对性去除所有 出版物 所携带的标签
    text = re.sub(r'<p class=".*?">', '', text)
    text = re.sub(r'<!--\?xml.*?>', '', text)
    text = re.sub(r'<link .*?/>', '', text)
    text = re.sub(r'<meta .*?/>', '', text)
    text = re.sub(r'<h1 .*?>', '', text)
    text = re.sub(r'<br/>', '', text)
    text = re.sub(r'<!DOCTYPE html .*?>', '', text)
    text = re.sub(r'<span .*?>', '', text)
    text = re.sub(r'<html .*?>', '', text)
    return text
