# Generated by Django 3.0.7 on 2020-08-13 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cardonalab', '0018_auto_20200716_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LibStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_id', models.PositiveSmallIntegerField()),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cardonalab.Library')),
            ],
        ),
    ]
