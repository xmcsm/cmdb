# Generated by Django 2.2.12 on 2020-06-12 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_auto_20200611_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='assettype',
            name='type_id',
            field=models.CharField(default=123, max_length=64, unique=True, verbose_name='资产编码'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='event_type',
            field=models.SmallIntegerField(choices=[(0, '其它'), (1, '硬件变更'), (2, '新增配件'), (3, '设备下线'), (4, '设备上线'), (5, '定期维护'), (6, '业务上线\\更新\\变更'), (7, '待审批资产变更'), (8, '软件变更'), (9, '资产类型变更')], default=4, verbose_name='事件类型'),
        ),
    ]
