import os
import shutil

from api.db.config import TEST_DATA_DIR, ERRORS_FILE_NAME


def create_test_files(test_name: str, test_kits: list[dict]) -> int:
    if not os.path.isdir(TEST_DATA_DIR):
        os.mkdir(TEST_DATA_DIR)

    path = os.path.join(TEST_DATA_DIR, test_name)
    if not os.path.isdir(path):
        os.mkdir(path)

    # Создание файлов с тестовыми данными.
    for i, test_kit in enumerate(test_kits):
        input_data = test_kit.get('input')
        output_data = test_kit.get('output')
        if not input_data or not output_data:
            return i

        with open(os.path.join(path, f'input-{i + 1}.txt'), 'w') as file:
            file.write(input_data)

        with open(os.path.join(path, f'output-{i + 1}.txt'), 'w') as file:
            file.write(output_data)

    return len(test_kits)


def get_tests_names():
    return os.listdir(TEST_DATA_DIR)


def test_exists(test_name: str):
    path = os.path.join(TEST_DATA_DIR, test_name)
    return os.path.exists(path)


def delete_test_files(test_name: str):
    path = os.path.join(TEST_DATA_DIR, test_name)
    if not os.path.isdir(path):
        return

    shutil.rmtree(path)


def get_errors() -> str | None:
    if not os.path.exists(ERRORS_FILE_NAME):
        return None

    with open(ERRORS_FILE_NAME, 'r') as file:
        return file.read().encode('utf-8').decode('utf-8') or None


def clear_errors():
    with open(ERRORS_FILE_NAME, 'w') as file:
        file.write('')
