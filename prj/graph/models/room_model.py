import json
import requests
from django.db import models
from graph import consts

# Create your models here.
class Room(models.Model):
    class Meta:
        verbose_name = 'ルーム'
        verbose_name_plural = 'ルーム一覧'
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'room_id'],
                name='room_unique',
            ),
        ]

    event = models.ForeignKey(
        'graph.SREvent',
        verbose_name='SRイベント',
        on_delete=models.CASCADE,
        related_name='room',
    )
    name = models.CharField(
        verbose_name='ルーム名',
        max_length=128,
    )
    room_id = models.IntegerField(
        verbose_name='ルームID',
    )
    point = models.JSONField(
        verbose_name='ポイント',
        default=list,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name or 'Room(No Name)'

    @property
    def last_point(self):
        if type(self.point) == list:
            if self.point:
                return self.point[-1]
        return 0

    def make_dataset(self):
        # グラフ用のデータセットを作成
        dataset = {
          "label": self.name,
          "data": self.point,
          "borderWidth": 1,
          "pointRadius": 0,
          "lineTension": 0,
          "pointHitRadius": 3,
          "pointHoverRadius": 2,
          "fill": False,
        }
        return dataset

    def get_point(self):
        # ポイント取得
        try:
            try:
                url = consts.API_ROOM_EVENT_AND_SUPPORT
                params = {
                    'room_id': self.room_id,
                }
                r = requests.get(url, params=params)
                r.raise_for_status()
                data = r.json()
                point = data["event"]["ranking"]["point"]
            except Exception as e:
                print(f'[ERROR][Room.get_point({self.room_id=})]ルーム参加イベント情報API実行時にエラーが発生しました。({e})')
                raise e

            point_list = self.point or []
            point_list.append(point)
            self.point = point_list
            self.save()
            print(f'[INFO][Room.get_point({self.room_id=})]ポイントを取得しました。({point=})')

        except Exception as e:
            print(f'[ERROR][Room.get_point({self.room_id=})]ポイント取得に失敗しました({e})')