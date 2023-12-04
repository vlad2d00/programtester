from rest_framework import mixins
from rest_framework.response import Response

from api.db.dao import get_test_request_queue_position
from api.db.operation import Operation
from api.models import TestFailed
from programtester.utils.log import log


def proc_request(operation: Operation):
    def inner(func):
        def wrapper(request, *args, **kwargs):
            response = func(request, *args, **kwargs)

            model = request.serializer_class.Meta.model
            if operation == Operation.CREATE:
                model_id = int(response.data.serializer.instance.pk)
            elif operation == Operation.LIST:
                model_id = None
            else:
                model_id = int(request.kwargs['pk'])

            log(request=request.request, operation=operation, model=model, model_id=model_id)
            return response

        return wrapper

    return inner


# ===============================================================
#                        Базовые миксины
# ===============================================================

class CreateModelMixin(mixins.CreateModelMixin):
    @proc_request(Operation.CREATE)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ListModelMixin(mixins.ListModelMixin):
    @proc_request(Operation.LIST)
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['results'] = self.proc_list_results(response.data['results'])
        return response

    def proc_list_results(self, results):
        return results


class RetrieveModelMixin(mixins.RetrieveModelMixin):
    @proc_request(Operation.GET)
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.proc_retrieve_response(response)

    def proc_retrieve_response(self, response: Response):
        return response


class UpdateModelMixin(mixins.UpdateModelMixin):
    @proc_request(Operation.UPDATE)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class DestroyModelMixin(mixins.DestroyModelMixin):
    @proc_request(Operation.DELETE)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ===============================================================
#                      Конкретные миксины
# ===============================================================

class ListTestMixin(ListModelMixin):
    def proc_list_results(self, results):
        instance = results.serializer.instance

        for i in range(len(results)):
            results[i]['count_test_data'] = len(instance[i].test_data)
            results[i].pop('test_data')
            results[i]['user'] = {
                'id': instance[i].user.id,
                'username': instance[i].user.username,
            }
        return results


class RetrieveTestRequestMixin(RetrieveModelMixin):
    def proc_retrieve_response(self, response: Response):
        if response.data['processed']:
            if not response.data['passed']:
                test_failed = TestFailed.objects.get(test_request_id=response.data.serializer.instance.id)
                if test_failed.test_data_number:
                    response.data['test_data_number'] = test_failed.test_data_number
                if test_failed.input_data:
                    response.data['input_data'] = test_failed.input_data
                if test_failed.expected_output_data:
                    response.data['expected_output_data'] = test_failed.expected_output_data
                if test_failed.received_output_data:
                    response.data['received_output_data'] = test_failed.received_output_data
                if test_failed.errors:
                    response.data['errors'] = test_failed.errors
        else:
            return Response({
                'datetime_create': response.data['datetime_create'],
                'processed': response.data['processed'],
                'queue_position': get_test_request_queue_position(
                    test_request_id=response.data.serializer.instance.pk),
            })

        return response
