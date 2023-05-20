from django.contrib import admin
from graph.models import SREvent, Room

# Register your models here.
@admin.action(description='イベント初期化')
def srevent_initialize(modeladmin, request, queryset):
    for obj in queryset:
        obj.initialize()

class SREventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_id', 'start_dt', 'end_dt', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'event_id',)
    actions = [srevent_initialize]  # 定義した関数などをリストアップ
    actions_on_top = True  # ページ上部に表示

admin.site.register(SREvent, SREventAdmin)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_id', 'event', 'last_point', )
    list_filter = ('event',)
    search_fields = ('name', 'room_id',)

    def last_point(self, obj):
        return obj.last_point

    last_point.short_description = '最終ポイント'

admin.site.register(Room, RoomAdmin)
