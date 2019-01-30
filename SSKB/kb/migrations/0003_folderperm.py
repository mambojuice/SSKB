# Generated by Django 2.1.2 on 2019-01-14 13:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('kb', '0002_auto_20181209_2034'),
    ]

    operations = [
        migrations.CreateModel(
            name='FolderPerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=2)),
                ('folder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kb.Folder')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
    ]