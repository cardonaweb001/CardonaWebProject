# Generated by Django 4.0.6 on 2022-07-31 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cardonalab', '0028_alter_librarybulkdataload_boxno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarybulkdataload',
            name='essential',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='librarybulkdataload',
            name='growthDefense',
            field=models.CharField(max_length=255),
        ),
    ]