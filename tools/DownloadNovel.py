import re
import os
import time
import tools
import threading
import requests
from urllib.parse import urljoin
from webdav4.client import Client
from . import Fanqie
from ebooklib import epub
from Api.models import History
from pathlib import Path


class DownloadNovel(threading.Thread):
    """
    下载小说，应传入番茄对象
    """

    def __init__(self, fanqie: Fanqie):
        # 番茄小说对象
        self.fanqie: Fanqie = fanqie
        # 停止子进程
        self._stop_flag = False
        self._stop_event = threading.Event()

        # 自定义WebDav路径
        self.is_webdav = os.environ.get('IS_WEBDAV')
        if self.is_webdav:
            self.webdav_username = os.environ.get('WEBDAV_USERNAME')
            self.webdav_pwd = os.environ.get('WEBDAV_PWD')
            self.webdav_url = os.environ.get('WEBDAV_URL')
            self.webdav = Client(base_url=self.webdav_url,
                                 auth=(self.webdav_username, self.webdav_pwd))
            tools.logger.info(f'已成功加载webdav服务器({self.webdav_url})')

        # 自定义保存路径
        self.custom_path = os.environ.get('CUSTOM_PATH')
        if not self.custom_path:
            self.custom_path = '/root/alist/book/books'

        super().__init__()

    def run(self) -> None:
        # 数据库中获取小说对象
        history_entry = History.objects.get(obid=self.fanqie.obid)
        tools.logger.info(f'开始下载小说: \n{self.fanqie.__str__()}')

        # 判断下载模式
        if self.fanqie.mode == 'txt':
            tools.logger.info(f'正在以txt模式下载小说')

            content = f"""{self.fanqie.title}
            {self.fanqie.intro}
            """
            # 获取所有章节链接
            start_index = 0

            file_name = self.fanqie.title + ".txt"
            file_path = os.path.join(self.custom_path, file_name)

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
                                tools.logger.error('错误！{e}')
                            else:
                                break
                            retry_get_api += 1

                        if "data" in api_data and "content" in api_data["data"]:
                            chapter_content = api_data["data"]["content"]
                            break  # 如果成功获取章节内容，跳出重试循环
                        else:
                            if retry_count == 1:
                                tools.logger.warning(f'{chapter_title} 获取失败，正在尝试重试...')
                            tools.logger.warning(f'第 ({retry_count}/3) 次重试获取章节内容')
                            retry_count += 1  # 否则重试

                    if retry_count == 4:
                        tools.logger.error(f'无法获取章节内容: {chapter_title}，跳过。')
                        continue  # 重试次数过多后，跳过当前章节

                    # 提取文章标签中的文本
                    chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)

                    # 将 <p> 标签替换为换行符
                    chapter_text = re.sub(r"<p>", "\n", chapter_text)

                    # 去除其他 html 标签
                    chapter_text = re.sub(r"</?\w+>", "", chapter_text)

                    chapter_text = tools.fix_publisher(chapter_text)

                    # 在小说内容字符串中添加章节标题和内容
                    content += f"\n\n\n{chapter_title}\n{chapter_text}"

                    chapter_num_now += 1
                    history_entry.percent = round(
                        (chapter_num_now / chapter_num) * 100, 2)
                    history_entry.save()

                    # 打印进度信息
                    tools.logger.info(f'已获取 {chapter_title}, 进度：{history_entry.percent}%')
                # 根据编码转换小说内容字符串为二进制数据
                data = content.encode('utf-8', errors='ignore')

                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(data)

                file_path = os.path.join(self.custom_path, file_name)
                file_path = Path(file_path)
                if self.is_webdav:
                    self.webdav.upload_file(from_path=file_path,
                                            to_path=os.path.join('/public', file_name),
                                            overwrite=True)
                    tools.logger.info(f'《{self.fanqie.title}》已成功上传webdav服务器')

                # 打印完成信息
                tools.logger.info(f'已保存{self.fanqie.title}.txt至本地')

            except BaseException as e:
                # 捕获所有异常，及时保存文件
                tools.logger.error(f'发生异常: \n{e}')
                tools.logger.info('正在尝试保存文件')
                # 根据编码转换小说内容字符串为二进制数据
                data = content.encode('utf-8', errors='ignore')

                # 保存文件
                file_path = os.path.join(self.custom_path, file_name)
                with open(file_path, "wb") as f:
                    f.write(data)

                tools.logger.info('文件已保存！')
                return

        elif self.fanqie.mode == 'epub':
            tools.logger.info(f'正在以epub模式下载小说')

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
            intro_e.content = (f'<img src="image.jpg" alt="Cover Image"/>'
                               f'<h1>{self.fanqie.title}</h1>'
                               f'<p>{self.fanqie.intro}</p>')
            book.add_item(intro_e)

            font_file = "tools/assets/Xingyv-Regular.ttf"
            css1_file = "tools/assets/page_styles.css"
            css2_file = "tools/assets/stylesheet.css"
            # 打开资源文件
            with open(font_file, 'rb') as f:
                font_content = f.read()
            with open(css1_file, 'r', encoding='utf-8') as f:
                css1_content = f.read()
            with open(css2_file, 'r', encoding='utf-8') as f:
                css2_content = f.read()

            # 创建一个EpubItem实例来存储你的字体文件
            font = epub.EpubItem(
                uid="font",
                file_name="fonts/Xingyv-Regular.ttf",  # 这将是字体文件在epub书籍中的路径和文件名
                media_type="application/x-font-ttf",
                content=font_content,
            )
            # 创建一个EpubItem实例来存储你的CSS样式
            nav_css1 = epub.EpubItem(
                uid="style_nav1",
                file_name="style/page_styles.css",  # 这将是CSS文件在epub书籍中的路径和文件名
                media_type="text/css",
                content=css1_content,
            )
            nav_css2 = epub.EpubItem(
                uid="style_nav2",
                file_name="style/stylesheet.css",  # 这将是CSS文件在epub书籍中的路径和文件名
                media_type="text/css",
                content=css2_content,
            )

            # 将资源文件添加到书籍中
            book.add_item(font)
            book.add_item(nav_css1)
            book.add_item(nav_css2)

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
                    tools.logger.info(f'正在获取{volume_title}')
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
                                    tools.logger.error(f'发生异常: \n{e}')
                                else:
                                    break
                                retry_get_api += 1

                            if "data" in api_data and "content" in api_data["data"]:
                                chapter_content = api_data["data"]["content"]
                                break  # 如果成功获取章节内容，跳出重试循环
                            else:
                                if retry_count == 1:
                                    tools.logger.warning(f'{chapter_title} 获取失败，正在尝试重试...')
                                tools.logger.warning(f'第 ({retry_count}/3) 次重试获取章节内容')
                                retry_count += 1  # 否则重试

                        if retry_count == 4:
                            tools.logger.error(f'无法获取章节内容: {chapter_title}，跳过。')
                            continue  # 重试次数过多后，跳过当前章节

                        # 提取文章标签中的文本
                        chapter_text = re.search(r"<article>([\s\S]*?)</article>", chapter_content).group(1)

                        # 在小说内容字符串中添加章节标题和内容
                        text = epub.EpubHtml(title=chapter_title,
                                             file_name=f'chapter_{volume_id}_{chapter_id_name}.xhtml')
                        # 加入css
                        # 加入css
                        text.add_item(nav_css1)
                        text.add_item(nav_css2)

                        text.content = (f'<h2 class="titlecss">{chapter_title}</h2>'
                                        f'{chapter_text}')

                        toc_index = toc_index + (text,)
                        book.spine.append(text)

                        # 寻找第一章
                        if chapter_id_name == 1:
                            first_chapter = f'chapter_{volume_id}_{chapter_id_name}.xhtml'

                        # 加入epub
                        book.add_item(text)

                        chapter_num_now += 1
                        history_entry.percent = round(
                            (chapter_num_now / chapter_num) * 100, 2)
                        history_entry.save()

                        # 打印进度信息
                        tools.logger.info(f'已获取 {chapter_title}, 进度：{history_entry.percent}%')
                    # 加入书籍索引
                    book.toc = book.toc + ((epub.Section(volume_title, href=first_chapter),
                                            toc_index,),)
            # 捕获异常
            except BaseException as e:
                # 捕获所有异常
                tools.logger.error(f'发生异常: \n{e}')
                return

            # 添加 navigation 文件
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # 拼接文件名和文件路径
            file_name = self.fanqie.title + ".epub"
            file_path = os.path.join('/root/alist/book/books', file_name)

            # 书写电子书
            epub.write_epub(file_path, book, {})

            # webdav上传
            file_path = Path(file_path)
            if self.is_webdav:
                self.webdav.upload_file(from_path=file_path,
                                        to_path=os.path.join('/public', file_name),
                                        overwrite=True)
                tools.logger.info(f'《{self.fanqie.title}》已成功上传webdav服务器')

            tools.logger.info(f'已保存{self.fanqie.title}.epub至本地')

    # 停止子进程函数
    def stop(self):
        self._stop_event.set()
