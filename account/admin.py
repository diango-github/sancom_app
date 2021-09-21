from django.contrib import admin

from .models import User, File, Dictionary, Erepeat, Crepeat, E3sentences, C3sentences, Edeepen, Cdeepen, Efinish, Cfinish

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