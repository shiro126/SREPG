# Generated by Django 4.1 on 2023-05-20 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph', '0002_alter_srevent_remark_alter_srevent_schedule'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='room',
            constraint=models.UniqueConstraint(fields=('event', 'room_id'), name='room_unique'),
        ),
    ]
