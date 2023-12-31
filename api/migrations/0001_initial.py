# Generated by Django 4.1.4 on 2023-12-03 21:08

import api.models
import api.validators
from django.conf import settings
import django.core.files.utils
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramLang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=70, validators=[django.core.validators.MaxLengthValidator(70)], verbose_name='Имя')),
            ],
            options={
                'verbose_name': 'Язык программирования',
                'verbose_name_plural': 'Языки программирования',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=70, verbose_name='Название')),
                ('datetime_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('test_data', models.JSONField(encoder=api.models.PrettyJSONEncoder, validators=[api.validators.validate_test_data], verbose_name='Тестовые данные')),
                ('time_limit', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(60.0)], verbose_name='Ограничение по времени')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
                'ordering': ['-datetime_create'],
            },
        ),
        migrations.CreateModel(
            name='TestRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('processed', models.BooleanField(default=False, editable=False, verbose_name='Обработано')),
                ('passed', models.BooleanField(default=False, editable=False, verbose_name='Пройдено')),
                ('total_time', models.FloatField(default=0.0, editable=False, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Общее время')),
                ('count_tests_passed', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Пройдено тестов')),
                ('total_tests', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Всего тестов')),
                ('files', models.JSONField(encoder=api.models.PrettyJSONEncoder, validators=[api.validators.validate_test_files], verbose_name='Файлы')),
                ('main_file_name', models.CharField(max_length=255, validators=[django.core.files.utils.validate_file_name], verbose_name='Имя главного файла')),
                ('program_lang', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='api.programlang', verbose_name='Язык программирования')),
                ('test', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='api.test', verbose_name='Тест')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Запрос на тестирование',
                'verbose_name_plural': 'Запросы на тестирования',
                'ordering': ['-datetime_create'],
            },
        ),
        migrations.CreateModel(
            name='TestFailed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_data_number', models.PositiveIntegerField(blank=True, editable=False, null=True, verbose_name='Номер тестовых данных')),
                ('input_data', models.TextField(blank=True, editable=False, null=True, verbose_name='Входные данные')),
                ('expected_output_data', models.TextField(blank=True, editable=False, null=True, verbose_name='Ожидаемые выходные данные')),
                ('received_output_data', models.TextField(blank=True, editable=False, null=True, verbose_name='Полученные выходные данные')),
                ('errors', models.TextField(blank=True, editable=False, null=True, verbose_name='Ошибки')),
                ('test_request', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='api.testrequest', verbose_name='Запрос на тестирование')),
            ],
            options={
                'verbose_name': 'Проваленный тест',
                'verbose_name_plural': 'Проваленные тесты',
            },
        ),
        migrations.AddIndex(
            model_name='testrequest',
            index=models.Index(fields=['-datetime_create'], name='api_testreq_datetim_5068c0_idx'),
        ),
        migrations.AddIndex(
            model_name='test',
            index=models.Index(fields=['-datetime_create'], name='api_test_datetim_d67ee3_idx'),
        ),
    ]
