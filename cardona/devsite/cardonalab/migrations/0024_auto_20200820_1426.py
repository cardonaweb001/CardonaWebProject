# Generated by Django 3.0.7 on 2020-08-20 19:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cardonalab', '0023_auto_20200819_1302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chemical',
            options={'verbose_name_plural': '          Chemicals'},
        ),
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name_plural': '   Libraries'},
        ),
        migrations.AlterModelOptions(
            name='manufacturer',
            options={'verbose_name_plural': '         Manufacturers'},
        ),
        migrations.AlterModelOptions(
            name='plasmid',
            options={'verbose_name_plural': '      Plasmids'},
        ),
        migrations.AlterModelOptions(
            name='primer',
            options={'verbose_name_plural': '       Primers'},
        ),
        migrations.AlterModelOptions(
            name='stock',
            options={'verbose_name_plural': '    Stocks'},
        ),
        migrations.AlterModelOptions(
            name='storagelocation',
            options={'verbose_name_plural': '        Storage Locations'},
        ),
        migrations.AlterModelOptions(
            name='strain',
            options={'verbose_name_plural': '     Strains'},
        ),
        migrations.CreateModel(
            name='Genome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '  Genomes',
            },
        ),
    ]
