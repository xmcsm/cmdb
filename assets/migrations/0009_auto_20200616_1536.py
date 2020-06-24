# Generated by Django 2.2.12 on 2020-06-16 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0008_auto_20200615_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='software',
            name='assets',
        ),
        migrations.AddField(
            model_name='software',
            name='assets',
            field=models.ManyToManyField(blank=True, null=True, to='assets.Asset', verbose_name='所属资产'),
        ),
    ]