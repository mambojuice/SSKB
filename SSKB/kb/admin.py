from django.contrib import admin
from .models import Folder, Log, Article, History

admin.site.register(Folder)
admin.site.register(Log)
admin.site.register(Article)
admin.site.register(History)

class LogAdmin(admin.ModelAdmin):
    readonly_fields=['timestamp', 'message']
