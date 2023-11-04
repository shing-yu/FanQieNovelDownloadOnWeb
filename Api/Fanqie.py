import re
import json
import time
import requests
from bs4 import BeautifulSoup
import threading
from .models import History


class Fanqie:
    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 "
          "Safari/537.36 Edg/119.0.0.0")
    headers = {
        "User-Agent": ua
    }

    def __init__(self, url):
        response = requests.get(url, headers=self.headers)
        self.html = response.text
        self.book_id = re.search(r"/(\d+)", url).group(1)

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
    def __init__(self, fanqie: object, mode):
        self.fanqie = fanqie
        self.mode = mode
        self._stop_flag = False
        self._stop_event = threading.Event()
        super().__init__()

    def run(self) -> None:
        history_entry = History.objects.get(book_id=self.fanqie.book_id)
        for i in range(100):
            if self._stop_event.is_set(): break
            time.sleep(1)
            if self._stop_event.is_set(): break
            history_entry.percent += 1
            history_entry.save()
            print(history_entry.percent)
        history_entry.delete()
        print(self.fanqie)
        if self.mode == 'txt':
            print('txt模式')
        elif self.mode == 'epub':
            print('epub模式')

    def stop(self):
        self._stop_event.set()
