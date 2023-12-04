from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from api import signals
from api.db.init_db import init_db
from api.db.testing_program import start_thread_proc_queue_test
from api.paginations import TestViewSetPagination
from api.permissions import IsAdminOrOwnerOrReadOnly
from api.serializers import *
from api.mixins import *

if INIT_DB:
    init_db()

signals.signals()

start_thread_proc_queue_test()


class TestViewSet(CreateModelMixin,
                  UpdateModelMixin,
                  RetrieveModelMixin,
                  ListTestMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    serializer_class = TestSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    pagination_class = TestViewSetPagination

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return Test.objects.filter(pk=pk)

        serializer = ListTestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data.get('user_id')

        q = Q()
        if user_id:
            q &= Q(user_id=user_id)

        return Test.objects.filter(q)

    @action(methods=['post'], detail=True)
    def run(self, request: Request, pk: int):
        serializer = RunTestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        program_lang_name = serializer.validated_data['program_lang']
        try:
            program_lang = ProgramLang.objects.get(name=program_lang_name)
        except ProgramLang.DoesNotExist:
            return Response({'detail': f'Язык программирования {program_lang_name} не поддерживается'},
                            status=status.HTTP_400_BAD_REQUEST)

        test_request = TestRequest.objects.create(program_lang_id=program_lang.id,
                                                  files=serializer.validated_data['files'],
                                                  main_file_name=serializer.validated_data['main_file_name'],
                                                  user_id=request.user.id,
                                                  test_id=pk)

        return Response({
            'result_id': test_request.id,
            'queue_position': get_test_request_queue_position(test_request_id=test_request.id),
        })


class TestRequestViewSet(RetrieveTestRequestMixin,
                         GenericViewSet):
    serializer_class = TestRequestSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return TestRequest.objects.filter(pk=pk)
