# Generated by Django 4.0 on 2021-12-28 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_alter_player_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='sending_gift_date',
            field=models.TextField(verbose_name='Дата отправки подарков'),
        ),
    ]
