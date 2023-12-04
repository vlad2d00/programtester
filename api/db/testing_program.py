import os
import shutil
import psutil
import subprocess
from abc import abstractmethod
import time
from threading import Thread

from api.db.config import TEST_DATA_DIR, ERRORS_FILE_NAME, APP_DIR, MANIFEST_FILE_NAME, OUTPUT_FILE_NAME, \
    ProgramLangName
from api.db.dao import get_test_request_queue
from api.db.file_service import get_errors
from api.models import TestFailed, TestRequest

TEST_TIME_CHECK_FREQUENCY = 0.5
OUTPUT_STREAMS = ' 1> {} 2> {}'.format(OUTPUT_FILE_NAME, ERRORS_FILE_NAME)


class CompileException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class TimeoutException(Exception):
    def __init__(self, timeout: float, total_time: float = None):
        self.timeout = timeout
        self.total_time = total_time

    def __str__(self):
        return f'Ошибка времени исполнения: время работы программы превысило {round(self.timeout, 3)} сек.'


class Program:
    def __init__(self, files: dict, main_file_name: str):
        self.files = {}
        self.main_file_name = main_file_name

        for key in files.keys():
            self.files[os.path.join(APP_DIR, key)] = files[key]

    @abstractmethod
    def compile(self):
        pass

    @abstractmethod
    def get_execute_command(self, input_file_name: str) -> str:
        pass

    def execute(self, input_file_name: str, timeout: float):
        def kill(proc_pid):
            process = psutil.Process(proc_pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()

        p = subprocess.Popen(self.get_execute_command(input_file_name) + OUTPUT_STREAMS, shell=True)
        try:
            p.wait(timeout)
        except subprocess.TimeoutExpired:
            kill(p.pid)
            raise TimeoutException(timeout)

    def run_testing(self,
                    test_name: str,
                    timeout: float,
                    count_test_data: int,
                    test_request: TestRequest = None
                    ) -> dict:
        path_test_name = os.path.join(TEST_DATA_DIR, test_name)
        total_time = 0
        i = 0

        while i < count_test_data:
            input_file_name = os.path.join(path_test_name, f'input-{i}.txt')
            output_file_name = os.path.join(path_test_name, f'output-{i}.txt')

            # Запуск кода программы.
            start_time = time.time()
            try:
                self.execute(input_file_name=input_file_name, timeout=timeout)
            except TimeoutException as e:
                raise TimeoutException(timeout=e.timeout, total_time=round(total_time + time.time() - start_time, 3))
            total_time += time.time() - start_time

            errors = get_errors()
            if errors:
                return {
                    'passed': False,
                    'total_time': round(total_time, 3),
                    'test_data_number': i + 1,
                    'errors': errors,
                }

            # Проверка результата работы программы.
            with open(OUTPUT_FILE_NAME, 'r') as file:
                received_output_data = file.read().split()
            with open(output_file_name, 'r') as file:
                expected_output_data = file.read().split()

            if expected_output_data != received_output_data:
                # Полученные выходные данные не равны ожидаемым.
                with open(input_file_name, 'r') as file:
                    input_data = file.read().split()

                return {
                    'passed': False,
                    'total_time': round(total_time, 3),
                    'test_data_number': i + 1,
                    'input_data': ' '.join(input_data),
                    'expected_output_data': ' '.join(expected_output_data),
                    'received_output_data': ' '.join(received_output_data),
                }

            i += 1
            if test_request:
                test_request.count_tests_passed = i
                test_request.save()

        return {
            'passed': True,
            'total_time': round(total_time, 3),
        }


class JavaProgram(Program):
    def __init__(self, files: dict, main_file_name: str):
        super().__init__(files, main_file_name)
        self.main_class_name = None

    def compile(self):
        # Удаление файлов предыдущего приложения.
        if os.path.exists(APP_DIR):
            shutil.rmtree(APP_DIR)

        # Создание файлов с кодом.
        for file_name in self.files.keys():
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'w') as file:
                file.write(self.files[file_name])

        # Компиляция файлов с кодом.
        command = 'javac ' + ' '.join([x for x in self.files.keys()])
        os.system(command + OUTPUT_STREAMS)

        errors = get_errors()
        if errors:
            raise CompileException(errors)

        main_file_name = os.path.join(APP_DIR, self.main_file_name)
        main_path = os.path.dirname(main_file_name)
        main_package = '.'.join(main_file_name.split('/')[:-1])
        self.main_class_name = main_file_name.split('/')[-1].split('.')[-2]
        main_class_full = (main_package + '.' if main_package else '') + self.main_class_name

        # Создание файла манифеста.
        with open(os.path.join(main_path, MANIFEST_FILE_NAME), 'w') as file:
            file.write('Manifest-Version: 1.0\nMain-Class: ' + main_class_full + '\n')

        # Компиляция jar-файла.
        jar_file_name = os.path.join(main_path, self.main_class_name + '.jar')
        command = 'jar cvmf ' + os.path.join(main_path, MANIFEST_FILE_NAME) + ' ' + jar_file_name
        for file_name in self.files.keys():
            command += ' ' + ''.join(file_name.split('.')[:-1]) + '.class'

        os.system(command + OUTPUT_STREAMS)
        errors = get_errors()
        if errors:
            raise CompileException(errors)

    def get_execute_command(self, input_file_name: str) -> str:
        return 'java -cp ' + APP_DIR[:-1] + ' ' + self.main_class_name + ' 0< ' + input_file_name
        # return ('java -cp ' + APP_DIR[:-1] + ' ' + self.main_class_name +
        #         ' 0< ' + input_file_name + self.OUTPUT_STREAMS)


PROGRAM_CLASS_DICTIONARY = {
    ProgramLangName.JAVA: JavaProgram
}


def get_program_lang_by_value(value: str) -> ProgramLangName | None:
    values = [x.value for x in ProgramLangName]
    if value not in values:
        return None
    return ProgramLangName.__getitem__(value.upper())


def proc_queue_test():
    # Вечный процесс мониторинга очереди программ на тестирование.
    while True:
        test_request_queue = get_test_request_queue()

        if test_request_queue:
            # Тестирование программы.
            test_request = test_request_queue[0]
            get_program_lang = get_program_lang_by_value(test_request.program_lang.name)
            program_class = PROGRAM_CLASS_DICTIONARY[get_program_lang]
            program = program_class(files=test_request.files, main_file_name=test_request.main_file_name)

            try:
                program.compile()

                count_test_data = len(test_request.test.test_data)
                test_request.total_tests = count_test_data
                test_request.save()

                result = program.run_testing(test_name=test_request.test.name,
                                             timeout=test_request.test.time_limit,
                                             count_test_data=count_test_data,
                                             test_request=test_request)

            except Exception as e:
                TestFailed.objects.create(errors=str(e), test_request=test_request)
                test_request.processed = True
                test_request.passed = False

                if type(e) == TimeoutException:
                    e: TimeoutException = e
                    test_request.total_time = e.total_time

                test_request.save()
                continue

            passed = result['passed']
            if not passed:
                TestFailed.objects.create(test_data_number=result['test_data_number'],
                                          input_data=result.get('input_data'),
                                          expected_output_data=result.get('expected_output_data'),
                                          received_output_data=result.get('received_output_data'),
                                          errors=result.get('errors'),
                                          test_request_id=test_request.id)

            test_request.processed = True
            test_request.passed = passed
            test_request.total_time = result['total_time']
            test_request.save()

        time.sleep(TEST_TIME_CHECK_FREQUENCY)


def start_thread_proc_queue_test():
    Thread(target=proc_queue_test, daemon=True).start()
