# Generated by Django 2.2.12 on 2020-06-11 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_auto_20200611_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='software',
            name='software_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='assets.SoftwareType', verbose_name='软件类型'),
        ),
    ]
