# Generated by Django 3.0.4 on 2020-03-28 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0004_auto_20200328_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpref',
            name='microchipped',
            field=models.CharField(default='e', max_length=1),
        ),
    ]
