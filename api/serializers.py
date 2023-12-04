from rest_framework import serializers as s

from api.models import *


class TestSerializer(s.ModelSerializer):
    user = s.HiddenField(default=s.CurrentUserDefault())

    class Meta:
        model = Test
        fields = '__all__'


class TestRequestSerializer(s.ModelSerializer):
    user = s.HiddenField(default=s.CurrentUserDefault())

    class Meta:
        model = TestRequest
        fields = ('datetime_create', 'processed', 'passed', 'total_time', 'user', 'test')


class ListTestSerializer(s.Serializer):
    datetime_create_begin = s.DateTimeField(required=False)
    datetime_create_end = s.DateTimeField(required=False)
    user_id = s.IntegerField(required=False)


class RunTestSerializer(s.Serializer):
    main_file_name = s.CharField()
    program_lang = s.CharField()
    files = s.JSONField()
