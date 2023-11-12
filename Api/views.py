import os

from django.http import JsonResponse
from .Fanqie import Fanqie, DownloadNovel
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import History

# 下载的小说集合
download_object = []


@csrf_exempt  # 为了允许跨域请求，可选
@require_POST  # 确保只接受POST请求，可选
def download(request):  # 下载接口
    global download_object
    if request.method == 'POST':
        try:
            # 获取url数据
            data = json.loads(request.body.decode('utf-8'))
            urls = data.get('urls', [])

            # 获取下载方式
            format_ = data.get('format', 'txt')
            print(format_)

            # 获取书本信息
            book = []
            urls = list(set(urls))
            [book.append(Fanqie(url, format_)) for url in urls]

            # 查看重复下载的书籍
            return_url = []

            # 开启下载进程
            for i in book:
                print(i)
                try:
                    history_ = History.objects.get(obid=i.obid)
                    if history_.obid == i.obid:
                        print('重复提交！')
                        return_url.append(i.url)
                        continue
                except Exception as e:
                    print(e)
                b = History(book_id=i.book_id, obid=i.obid, file_name=f'{i.title}.{format_}', percent=0)
                b.save()
                d = DownloadNovel(i)
                download_object.append({'obid': i.obid, 'obj': d})
                d.start()

            # 返回成功和重复的数据
            response_data = {'message': 'Download request received', 'urls': urls, 'return': return_url}
            return JsonResponse(response_data, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def download_del(_request, pk):  # 删除任务中的小说
    global download_object
    try:
        history_ = History.objects.get(obid=pk)
        for i in download_object:
            if i['obid'] == pk:
                i['obj'].stop()
        history_.delete()
        response_data = {'status': 'ok'}
        return JsonResponse(response_data, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400)


@csrf_exempt  # 为了允许跨域请求，可选
def history(_request):  # 查询所有正在任务中的小说
    records = History.objects.all()
    response_data = {'history': []}
    for record in records:
        print(record.book_id)
        print(record.file_name)
        print(record.percent)
        response_data['history'].append({'book_id': record.book_id,
                                         'obid': record.obid,
                                         'file_name': record.file_name,
                                         'percent': record.percent})
    response_data['history'] = response_data['history'][::-1]
    return JsonResponse(response_data, status=200)


def history_id(_request, pk):  # 根据具体obid查询小说下载数据
    history_entry = History.objects.get(obid=pk)
    print(history_entry.percent)
    return JsonResponse({'percent': history_entry.percent}, status=200)


def get_config(_request):  # 获取默认的配置
    # 公开下载链接
    public_url = os.environ.get('PUBLIC_URL')

    # 默认下载模式
    default_download_mode = os.environ.get('DEFAULT_DMODE')
    if not default_download_mode:
        default_download_mode = 'epub'

    ret = {
        'download_url': public_url,
        'default_download_mode': default_download_mode
    }
    return JsonResponse(ret, status=200)
