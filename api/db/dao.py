from api.models import TestRequest


def get_test_request_queue() -> list[TestRequest]:
    return TestRequest.objects.filter(processed=False).order_by('datetime_create')


def get_test_request_queue_position(test_request_id: int) -> int:
    for i, test_request in enumerate(get_test_request_queue()):
        if test_request.id == test_request_id:
            return i + 1

    return 0
