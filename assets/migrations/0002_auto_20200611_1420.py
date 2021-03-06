# Generated by Django 2.2.12 on 2020-06-11 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=64, unique=True, verbose_name='资产类型')),
            ],
            options={
                'verbose_name': '资产类型',
                'verbose_name_plural': '资产类型',
            },
        ),
        migrations.CreateModel(
            name='SoftwareType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=64, unique=True, verbose_name='软件类型')),
            ],
            options={
                'verbose_name': '软件类型',
                'verbose_name_plural': '软件类型',
            },
        ),
        migrations.RemoveField(
            model_name='software',
            name='sub_asset_type',
        ),
        migrations.AlterField(
            model_name='asset',
            name='asset_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.AssetType', verbose_name='资产类型'),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='event_type',
            field=models.SmallIntegerField(choices=[(0, '其它'), (1, '硬件变更'), (2, '新增配件'), (3, '设备下线'), (4, '设备上线'), (5, '定期维护'), (6, '业务上线\\更新\\变更'), (7, '待审批资产变更'), (8, '软件变更')], default=4, verbose_name='事件类型'),
        ),
        migrations.AddField(
            model_name='software',
            name='software_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='assets.SoftwareType', verbose_name='软件类型'),
            preserve_default=False,
        ),
    ]
