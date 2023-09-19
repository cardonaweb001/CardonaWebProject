# Generated by Django 3.0.7 on 2020-06-12 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardonalab', '0002_chemical_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemical',
            name='number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='chemical',
            constraint=models.UniqueConstraint(fields=('label', 'number'), name='unique_code'),
        ),
    ]
