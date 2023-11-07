"""
URL configuration for FanQieNovelDownloadOnWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    # 下载接口
    path('down/', views.download),
    # 删除正在下载的小说
    path('down/del/<str:pk>/', views.download_del),
    # 查询正在下载的小说
    path('history/', views.history),
    # 查询具体的小说
    path('history/<str:pk>/', views.history_id),
    # 获取公网下载链接
    path('get_download_url/', views.get_download_uel),
    #    path('admin/', admin.site.urls),
]
