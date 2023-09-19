# Generated by Django 3.0.7 on 2020-08-13 17:24

import cardonalab.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cardonalab', '0020_auto_20200813_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libstock',
            name='forward_primer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cardonalab.Primer'),
        ),
        migrations.AlterField(
            model_name='libstock',
            name='plasmid_map',
            field=models.FileField(blank=True, null=True, upload_to=cardonalab.models._plasmidmap_upload_location),
        ),
    ]