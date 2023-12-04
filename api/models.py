import json

from django.contrib.auth.models import User
from django.core.files.utils import validate_file_name
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator
from django.db import models as m

from api.db.config import *
from api.validators import validate_test_data, validate_test_files


class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)


class Test(m.Model):
    name = m.CharField(max_length=NAME_MAX_LENGTH, db_index=True, verbose_name='Название')
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    test_data = m.JSONField(encoder=PrettyJSONEncoder, verbose_name='Тестовые данные',
                            validators=(validate_test_data,))
    time_limit = m.FloatField(verbose_name='Ограничение по времени',
                              validators=(MinValueValidator(0.0),
                                          MaxValueValidator(MAX_TIME_LIMIT),))

    user = m.ForeignKey(User, on_delete=m.CASCADE, verbose_name='Владелец')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['-datetime_create']
        indexes = [
            m.Index(fields=['-datetime_create']),
        ]


class ProgramLang(m.Model):
    name = m.SlugField(max_length=NAME_MAX_LENGTH, db_index=True, verbose_name='Имя')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = 'Языки программирования'
        ordering = ['name']


class TestRequest(m.Model):
    datetime_create = m.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')
    processed = m.BooleanField(default=False, editable=False, verbose_name='Обработано')
    passed = m.BooleanField(default=False, editable=False, verbose_name='Пройдено')
    total_time = m.FloatField(default=0.0, editable=False, verbose_name='Общее время',
                              validators=(MinValueValidator(0.0),))

    count_tests_passed = m.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Пройдено тестов')
    total_tests = m.PositiveIntegerField(null=True, blank=True, editable=False, verbose_name='Всего тестов')
    main_file_name = m.CharField(max_length=FILE_NAME_MAX_LENGTH, verbose_name='Имя главного файла',
                                 validators=(validate_file_name,))

    program_lang = m.ForeignKey(ProgramLang, on_delete=m.CASCADE, editable=False, verbose_name='Язык программирования')
    files = m.JSONField(encoder=PrettyJSONEncoder, verbose_name='Файлы', validators=(validate_test_files,))

    user = m.ForeignKey(User, on_delete=m.CASCADE, verbose_name='Владелец')
    test = m.ForeignKey(Test, on_delete=m.CASCADE, editable=False, verbose_name='Тест')

    def __str__(self):
        return 'id=' + str(self.id) + ' (' + str(self.test) + ')'

    class Meta:
        verbose_name = 'Запрос на тестирование'
        verbose_name_plural = 'Запросы на тестирования'
        ordering = ['-datetime_create']
        indexes = [
            m.Index(fields=['-datetime_create']),
        ]


class TestFailed(m.Model):
    test_data_number = m.PositiveIntegerField(null=True, blank=True, editable=False,
                                              verbose_name='Номер тестовых данных')
    input_data = m.TextField(null=True, blank=True, editable=False, verbose_name='Входные данные')
    expected_output_data = m.TextField(null=True, blank=True, editable=False, verbose_name='Ожидаемые выходные данные')
    received_output_data = m.TextField(null=True, blank=True, editable=False, verbose_name='Полученные выходные данные')
    errors = m.TextField(null=True, blank=True, editable=False, verbose_name='Ошибки')

    test_request = m.OneToOneField(TestRequest, on_delete=m.CASCADE, editable=False,
                                   verbose_name='Запрос на тестирование')

    def __str__(self):
        return 'id=' + str(self.id) + ' (' + str(self.test_request.test) + ')'

    class Meta:
        verbose_name = 'Проваленный тест'
        verbose_name_plural = 'Проваленные тесты'
