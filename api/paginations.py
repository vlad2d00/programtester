from rest_framework.pagination import LimitOffsetPagination

from api.db.config import TESTS_LIMIT_DEFAULT, TESTS_LIMIT_MAX


class TestViewSetPagination(LimitOffsetPagination):
    default_limit = TESTS_LIMIT_DEFAULT
    max_limit = TESTS_LIMIT_MAX
