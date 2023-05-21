import datetime
import requests
import copy
import pytz
import json
from bs4 import BeautifulSoup as bs
from django.db import models
from graph import consts

# Create your models here.
class SREvent(models.Model):
    class Meta:
        verbose_name = 'SRイベント'
        verbose_name_plural = 'SRイベント一覧'

    title = models.CharField(
        verbose_name='イベント名',
        max_length=128,
    )
    event_id = models.IntegerField(
        verbose_name='イベントID',
    )
    start_dt = models.DateTimeField(
        verbose_name='開始日時',
    )
    end_dt = models.DateTimeField(
        verbose_name='終了日時',
    )
    last_watch_dt = models.DateTimeField(
        verbose_name='最終観測日時',
        null=True,
        blank=True,
    )
    schedule = models.JSONField(
        verbose_name='スケジュール',
        default=list,
        null=True,
        blank=True,
    )
    remark = models.TextField(
        verbose_name='備考',
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(
        verbose_name='公開',
        default=False,
    )

    def __str__(self):
        return self.title or 'SREvent(No Name)'

    @property
    def start_dt_tz(self):
        return self.start_dt.astimezone(pytz.timezone('Asia/Tokyo'))

    @property
    def end_dt_tz(self):
        return self.end_dt.astimezone(pytz.timezone('Asia/Tokyo'))

    @property
    def schedule_json(self):
        return json.dumps(self.schedule)

    @property
    def room_ranking(self):
        room_list = sorted(
            self.room.all(),
            key=lambda x: x.last_point,
            reverse=True,
        )
        return room_list

    def make_datasets(self):
        # グラフ用のデータセットを作成
        room_list = [x for x in self.room.all() if x.last_point > 0]
        room_list = sorted(
            room_list,
            key=lambda x: x.last_point,
            reverse=True,
        )
        datasets = [x.make_dataset() for x in room_list]
        return json.dumps(datasets)

    def initialize(self):
        # イベント開始前の初期化処理
        try:
            print(f'[INFO][SREvent.initialize({self.event_id=})]イベント初期化処理を開始します')
            from graph.models import Room
            room_id_list = []
            next_page = 1
            while next_page:
                try:
                    url = consts.API_EVENT_ROOM_LIST
                    params = {
                        'event_id': self.event_id,
                        'p': next_page,
                    }
                    r = requests.get(url, params=params)
                    r.raise_for_status()
                    data = r.json()
                except Exception as e:
                    print(f'[ERROR][SREvent.initialize({self.event_id=})]イベント参加ルーム一覧API実行時にエラーが発生しました。({e})')
                    raise e

                soup = bs(data['html'], 'html.parser')
                a_list = soup.find_all('a')
                for a in a_list:
                    try:
                        room_id_list.append(a.attrs['data-room-id'])
                    except Exception:
                        pass

                next_page = data['next_page']

            for room_id in room_id_list:
                try:
                    url = consts.API_ROOM_PROFILE
                    params = {
                        'room_id': room_id,
                    }
                    r = requests.get(url, params=params)
                    r.raise_for_status()
                    room_info = r.json()
                except Exception as e:
                    print(f'[ERROR][SREvent.initialize({self.event_id=})]ルーム情報API実行時にエラーが発生しました。({e})')
                    raise e

                try:
                    room, is_created = Room.objects.get_or_create(
                        event=self,
                        room_id=room_id,
                    )
                    if is_created:
                        room.name = room_info['room_name'].split('@')[0]
                        room.save()
                except Exception as e:
                    print(f'[ERROR][SREvent.initialize({self.event_id=})]ルームモデル登録時にエラーが発生しました。({e})')
                    raise e

            # スケジュールを登録する
            schedule_list = []
            time = self.start_dt_tz
            q_hour = datetime.timedelta(minutes=15)

            while time < self.end_dt:
                schedule_list.append(time.strftime('%m/%d %H:%M'))
                time = time + q_hour

            schedule_list.append(self.end_dt_tz.strftime('%m/%d %H:%M'))

            self.schedule = schedule_list
            # 公開済にする
            self.is_published = True
            self.save()

            print(f'[INFO][SREvent.initialize({self.event_id=})]イベント初期化処理を終了します')

        except Exception as e:
            print(f'[ERROR][SREvent.initialize({self.event_id=})]イベント初期化処理に失敗しました({e})')

    def get_point(self, now_dt):
        # ポイント取得
        for room in self.room.all():
            room.get_point()
        self.last_watch_dt = now_dt
        self.save()
