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
            [book.append(Fanqie(url, format_)) for url in urls]
            return_url = []
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
            # 在这里处理URLs，您可以执行下载操作或其他所需的操作
            response_data = {'message': 'Download request received', 'urls': urls, 'return': return_url}
            return JsonResponse(response_data, status=200, headers={'Access-Control-Allow-Origin': '*'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500, headers={'Access-Control-Allow-Origin': '*'})
    return JsonResponse({'error': 'Invalid request method'}, status=405, headers={'Access-Control-Allow-Origin': '*'})


def download_del(request, pk):
    global download_object
    try:
        history_ = History.objects.get(obid=pk)
        for i in download_object:
            if i['obid'] == pk:
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
                                         'obid': record.obid,
                                         'file_name': record.file_name,
                                         'percent': record.percent})
    response_data['history'] = response_data['history'][::-1]
    # print(type(response_data['history']))
    return JsonResponse(response_data, status=200, headers={'Access-Control-Allow-Origin': '*'})


def history_id(request, pk):
    history_entry = History.objects.get(obid=pk)
    print(history_entry.percent)
    return JsonResponse({'percent': history_entry.percent}, status=200, headers={'Access-Control-Allow-Origin': '*'})
