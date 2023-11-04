import threading
import time


class DownloadNovel(threading.Thread):
    def __init__(self):
        self._stop_event = threading.Event()
        super().__init__()

    def run(self) -> None:
        a = 0
        for i in range(100):
            if self._stop_event.is_set(): break
            time.sleep(1)
            if self._stop_event.is_set(): break
            a += 1
            print(a)

    def stop(self):
        self._stop_event.set()


a = DownloadNovel()
a.start()
print('a')
time.sleep(5)
a.stop()
print('b')
