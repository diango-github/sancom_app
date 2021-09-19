from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import Lan_appView2, business, econtents, erepeat, escraper, eseparate, ccontents, crepeat, cscraper, cseparate, trainingbox, en_repeat_list, ch_repeat_list, en_repeat, ch_repeat, en_3sentences, ch_3sentences, en_deepen_list, en_deepen, ch_deepen_list, ch_deepen, en_finish, ch_finish
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', business, name='business'),
    path('<int:num>', business, name='business'),
    path('econtents/<int:id>', econtents, name='econtents'),
    path('erepeat/<int:id>', erepeat, name='erepeat'),
    path('escraper/<int:id>', escraper, name='escraper'),
    path('eseparate/<int:id>', eseparate, name='eseparate'),
    path('ccontents/<int:id>', ccontents, name='ccontents'),
    path('crepeat/<int:id>', crepeat, name='crepeat'),
    path('cscraper/<int:id>', cscraper, name='cscraper'),
    path('cseparate/<int:id>', cseparate, name='cseparate'),
    path('trainingbox', trainingbox, name='trainingbox'),
    path('en_repeat_list', en_repeat_list, name='en_repeat_list'),
    path('ch_repeat_list', ch_repeat_list, name='ch_repeat_list'),
    path('en_repeat/<int:id>', en_repeat, name='en_repeat'),
    path('ch_repeat/<int:id>', ch_repeat, name='ch_repeat'),
    path('en_3sentences', en_3sentences.as_view(), name='en_3sentences'),
    path('ch_3sentences', ch_3sentences.as_view(), name='ch_3sentences'),
    path('en_deepen_list', en_deepen_list.as_view(), name='en_deepen_list'),
    path('ch_deepen_list', ch_deepen_list.as_view(), name='ch_deepen_list'),    
    path('en_deepen', en_deepen.as_view(), name='en_deepen'),    
    path('ch_deepen', ch_deepen.as_view(), name='ch_deepen'),
    path('en_finish', en_finish.as_view(), name='en_finish'),
    path('ch_finish', ch_finish.as_view(), name='ch_finish'),
    url('publiccontents/', Lan_appView2.as_view(), name='publiccontents'),
]