import os
import shutil

os.system('cnpm run build')
os.remove('D:\\bc\\python\\FanQieNovelDownloadOnWeb')
shutil.copytree('D:\\bc\\html\\DownloadFanqiePassageInWeb\\dist\\assets',
                'D:\\bc\\python\\FanQieNovelDownloadOnWeb')
shutil.copytree('D:\\bc\\html\\DownloadFanqiePassageInWeb\\dist\\history',
                'D:\\bc\\python\\FanQieNovelDownloadOnWeb\\templates')
shutil.copy('D:\\bc\\html\\DownloadFanqiePassageInWeb\\dist\\history',
            'D:\\bc\\python\\FanQieNovelDownloadOnWeb\\templates')
