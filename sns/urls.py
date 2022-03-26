from django.urls import path
from django.conf.urls import url
#from .views import index, groups, add, creategroup, share, good, CreatePost
from .views import index, groups, add, creategroup, share, good, post

urlpatterns = [
    path('', index, name='index'),
    path('<int:page>', index, name='index'),
    path('groups', groups, name='groups'),
    path('add', add, name='add'),
    path('creategroup', creategroup, name='creategroup'),
    #path('post', CreatePost.as_view(), name='post'),
    path('post', post, name='post'),
    path('share/<int:share_id>', share, name='share'),
    path('good/<int:good_id>', good, name='good'),

]