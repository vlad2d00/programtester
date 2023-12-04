from django.contrib import admin

from api.models import *

admin.site.site_header = 'Панель администрирования'


class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'datetime_create', 'time_limit', 'count_test_data', 'user')
    list_display_links = ('id', 'name',)
    search_fields = ('name',)
    list_filter = ('user__username',)
    list_per_page = MAX_ROW_PER_PAGE_ADMIN

    @admin.display(description='Количество тестовых данных')
    def count_test_data(self, obj: Test):
        return str(len(obj.test_data))


class ProgramLangAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_per_page = MAX_ROW_PER_PAGE_ADMIN


class TestRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'datetime_create', 'processed', 'passed', 'total_time', 'program_lang',
                    'files_info', 'user', 'test')
    list_display_links = ('id', 'datetime_create',)
    list_filter = ('processed', 'passed', 'program_lang', 'user__username', 'test__name')
    list_per_page = MAX_ROW_PER_PAGE_ADMIN

    @admin.display(description='Информация о файлах')
    def files_info(self, obj):
        count_files = len(obj.files.keys())
        count_lines = sum([obj.files[key].count('\n') + 1 for key in obj.files.keys()])
        files_size = round(sum([len(obj.files[key]) for key in obj.files.keys()]) / 1000, 2)
        return (f'Файлов: {count_files}; '
                f'Строк: {count_lines}; '
                f'Общий размер: {files_size} Кб;')


class TestFailedAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_data_number', 'input_data', 'expected_output_data', 'received_output_data',
                    'errors', 'test_request')
    list_filter = ('test_request__test__name',)
    list_per_page = MAX_ROW_PER_PAGE_ADMIN


admin.site.register(Test, TestAdmin)
admin.site.register(ProgramLang, ProgramLangAdmin)
admin.site.register(TestRequest, TestRequestAdmin)
admin.site.register(TestFailed, TestFailedAdmin)
