from django.http import JsonResponse
from .Fanqie import Fanqie
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from threading import Thread
from .models import History


@csrf_exempt  # 为了允许跨域请求，可选
@require_POST  # 确保只接受POST请求，可选
def download(request):
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
                b = History(book_id=i.book_id, file_name=f'{i.title}.{format_}', percent=0)
                b.save()
            # 在这里处理URLs，您可以执行下载操作或其他所需的操作
            response_data = {'message': 'Download request received', 'urls': urls}
            return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


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
    return JsonResponse({'percent': history_entry.percent}, status=200, headers={'Access-Control-Allow-Origin': '*'})
