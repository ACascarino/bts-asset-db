# Generated by Django 3.0.3 on 2020-04-06 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bts_asset_db', '0009_auto_20200406_0129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='records',
            name='timestamp',
            field=models.DateTimeField(db_column='Timestamp'),
        ),
    ]