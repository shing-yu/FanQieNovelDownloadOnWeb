from django.http import JsonResponse
from .Fanqie import Fanqie, DownloadNovel
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import History

download_object = []


@csrf_exempt  # 为了允许跨域请求，可选
@require_POST  # 确保只接受POST请求，可选
def download(request):
    global download_object
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            urls = data.get('urls', [])
            format_ = data.get('format', 'txt')
            print(format_)
            book = []
            urls = list(set(urls))
            [book.append(Fanqie(url)) for url in urls]
            for i in book:
                try:
                    history_ = History.objects.get(book_id=i.book_id)
                    if history_.book_id == i.book_id:
                        print('重复提交！')
                        continue
                except Exception as e:
                    pass
                b = History(book_id=i.book_id, file_name=f'{i.title}.{format_}', percent=0)
                b.save()
                d = DownloadNovel(i, format_)
                download_object.append({'book_id': i.book_id, 'obj': d})
                d.start()
            # 在这里处理URLs，您可以执行下载操作或其他所需的操作
            response_data = {'message': 'Download request received', 'urls': urls}
            return JsonResponse(response_data, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def download_del(request, pk):
    global download_object
    try:
        history_ = History.objects.get(book_id=pk)
        for i in download_object:
            if i['book_id'] == pk:
                i['obj'].stop()
        history_.delete()
        response_data = {'status': 'ok'}
        return JsonResponse(response_data, status=200, headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'error': str(e)}, status=400,
                            headers={'Access-Control-Allow-Origin': '*'})


@csrf_exempt  # 为了允许跨域请求，可选
def history(request):
    records = History.objects.all()
    response_data = {'history': []}
    for record in records:
        print(record.book_id)
        print(record.file_name)
        print(record.percent)
        response_data['history'].append({'book_id': record.book_id,
                                         'file_name': record.file_name,
                                         'percent': record.percent})
    return JsonResponse(response_data, status=200, headers={'Access-Control-Allow-Origin': '*'})


def history_id(request, pk):
    history_entry = History.objects.get(book_id=pk)
    print(history_entry.percent)
    return JsonResponse({'percent': history_entry.percent}, status=200, headers={'Access-Control-Allow-Origin': '*'})
