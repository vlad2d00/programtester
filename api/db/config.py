import os
from enum import Enum

INIT_DB = True
# INIT_DB = False


# Файлы

TEST_DATA_DIR = 'data/'
APP_DIR = 'src/'

MANIFEST_FILE_NAME = 'MANIFEST.MF'
OUTPUT_FILE_NAME = os.path.join(APP_DIR, 'output.txt')
ERRORS_FILE_NAME = os.path.join(APP_DIR, 'errors.txt')

# Ограничение длины строк в БД

NAME_MAX_LENGTH = 70
FILE_NAME_MAX_LENGTH = 255
TEST_DATA_MAX_COUNT = 1000
MAX_TIME_LIMIT = 60.0


# Пагинация

TESTS_LIMIT_DEFAULT = 10
TESTS_LIMIT_MAX = 1000


# Админ панель

MAX_ROW_PER_PAGE_ADMIN = 30


# Перечисления

class ProgramLangName(Enum):
    JAVA = 'java'
