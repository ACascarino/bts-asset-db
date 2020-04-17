# Generated by Django 3.0.3 on 2020-04-08 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bts_asset_db', '0013_auto_20200408_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='serial_number',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='itemclass',
            name='make',
            field=models.TextField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='itemclass',
            name='model',
            field=models.TextField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='itemclass',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]