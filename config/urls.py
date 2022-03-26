"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from account.views import Top
from .views import emailfunc
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve  #追加
from django.conf.urls import url  #追加

urlpatterns = [
    path('', Top.as_view(), name='top'),
    path('admin/', admin.site.urls),
    path('accounts/', include('account.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sancom_free/', include('sancom_free.urls')),
    path('sns/', include('sns.urls')),
    path('email/', emailfunc),
    #url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  #追加
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)