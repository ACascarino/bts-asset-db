# Generated by Django 3.0.3 on 2020-06-24 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bts_asset_db', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tests',
            new_name='PatTest',
        ),
        migrations.RenameModel(
            old_name='Records',
            new_name='Record',
        ),
        migrations.RenameModel(
            old_name='Repairs',
            new_name='Repair',
        ),
        migrations.RenameModel(
            old_name='VisualTests',
            new_name='VisualTest',
        ),
    ]
