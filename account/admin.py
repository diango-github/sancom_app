from django.contrib import admin

from .models import User, File, Dictionary, Erepeat, Crepeat, E3sentences, C3sentences, Edeepen, Cdeepen, Efinish, Cfinish, Message, Friend, Group, Good

admin.site.register(User)
admin.site.register(File)
admin.site.register(Dictionary)
admin.site.register(Erepeat)
admin.site.register(Crepeat)
admin.site.register(E3sentences)
admin.site.register(C3sentences)
admin.site.register(Edeepen)
admin.site.register(Cdeepen)
admin.site.register(Efinish)
admin.site.register(Cfinish)

admin.site.register(Message)
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Good)