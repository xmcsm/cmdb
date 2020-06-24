# Generated by Django 2.2.12 on 2020-06-15 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_auto_20200612_0858'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubordinateUnits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='单位名称')),
            ],
            options={
                'verbose_name': '所属单位',
                'verbose_name_plural': '所属单位',
            },
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='event_type',
            field=models.SmallIntegerField(choices=[(0, '其它'), (1, '硬件变更'), (2, '新增配件'), (3, '设备下线'), (4, '设备上线'), (5, '定期维护'), (6, '业务上线\\更新\\变更'), (7, '待审批资产变更'), (8, '软件变更'), (9, '资产类型变更'), (10, '软件类型变更'), (11, '系统设置变更')], default=4, verbose_name='事件类型'),
        ),
        migrations.AlterField(
            model_name='newassetapprovalzone',
            name='asset_type',
            field=models.CharField(blank=True, default='server', max_length=64, null=True, verbose_name='资产类型'),
        ),
    ]
