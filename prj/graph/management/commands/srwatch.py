import time
import datetime
import pytz
from django.core.management.base import BaseCommand
from django.utils import timezone
from graph.models import SREvent, Room


class Command(BaseCommand):
    help = "SRイベントの監視"

    def handle(self, *args, **options):
        print('[INFO][SRイベント監視プロセス]SRイベントの監視を開始します。')
        while True:
            self.srwatch()
            time.sleep(5)

    def srwatch(self):
        now_dt = timezone.now().replace(second=0, microsecond=0)
        if True or now_dt.minute in [0, 15, 30, 45]:
            # イベント開始処理
            event_list = SREvent.objects.filter(is_published=False)
            for event in event_list:
                if now_dt < event.end_dt_tz:
                    # イベント終了していない
                    if event.start_dt_tz - timezone.timedelta(minutes=30) < now_dt:
                        # イベント開始30分前を過ぎている
                        event.initialize()

            # 開催中イベントのポイント取得
            event_list = SREvent.objects.filter(
                start_dt__lte=now_dt,
                end_dt__gte=now_dt,
                is_published=True,
                last_watch_dt__lt=now_dt,
            )
            print(event_list)
            for event in event_list:
                event.get_point(now_dt)

        elif now_dt.minute == 59:
            # 開催終了するイベントのポイント取得
            event_list = SREvent.objects.filter(
                end_dt=now_dt,
                is_published=True,
                last_watch_dt__lt=now_dt,
            )
            for event in event_list:
                event.get_point(now_dt)
