import json

from rest_framework.request import Request

from api.db.operation import Operation
from programtester.utils.datetime_service import datetime_to_string, datetime_now
from programtester.utils.request_service import get_request_ip_addr, get_request_user_agent


def get_request_params(request: Request, operation: Operation) -> str:
    if operation in (Operation.CREATE, Operation.GET, Operation.DELETE):
        return ''

    elif operation == Operation.UPDATE:
        keys = [key for key in request.data]
        if 'id' in keys:
            keys.remove('id')
        return ', '.join(keys)

    elif operation == Operation.LIST:
        params = {}
        for key in request.query_params.keys():
            params[key] = request.query_params[key][0]

        params_to_int = ('limit', 'offset')
        for name in params_to_int:
            value = params.get(name)
            if value:
                params[name] = int(value)

        return json.dumps(params)[1:-1]

    else:
        return json.dumps(request.data)[1:-1]


def log(request, operation: Operation, model, model_id: int = None):
    params = get_request_params(request, operation)

    print('[' + datetime_to_string(datetime_now()) + '] ' +
          operation.value + ' ' + model.__name__ + ' ' +
          (str(model_id) + ' ' if model_id else '') +
          (': ' + params + ' ' if params else '') + '| ' +
          get_request_ip_addr(request) + ' | ' +
          get_request_user_agent(request))
