# Generated by Django 3.0.7 on 2020-10-09 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bts_asset_db', '0009_auto_20201009_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testingmachine',
            name='serial_number',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='machine_serial_no',
            field=models.ForeignKey(db_column='machine_serial_no', on_delete=django.db.models.deletion.PROTECT, to='bts_asset_db.TestingMachine', to_field='serial_number'),
        ),
    ]
