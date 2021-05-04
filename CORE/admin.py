from django.contrib import admin
from .models import Media, Video


# Register your models here.
class MediaAdmin(admin.ModelAdmin):
    meta = Media
    list_display = ['name', 'tmdb_id', 'type']


class VideoAdmin(admin.ModelAdmin):
    meta = Video
    list_display = ['list', 'name', 'location', 'genre', 'type', 'tmdb_id', ]


admin.site.register(Media, MediaAdmin)
admin.site.register(Video, VideoAdmin)
