from django.core.exceptions import ValidationError
from django.core.files.utils import validate_file_name
from django.utils.translation import gettext_lazy as _


def validate_test_data(value):
    message = _("Тестовый набор должен состоять из списка словарей с ключами "
                "\"input\" и \"output\" и их строковыми значениями")
    code = "test_kits"

    if type(value) != list:
        raise ValidationError(message, code=code, params={"value": value})

    for item in value:
        input_data = item.get("input")
        output_data = item.get("output")
        if not input_data or not output_data or type(input_data) != str or type(output_data) != str:
            raise ValidationError(message, code=code, params={"value": value})


def validate_test_files(value):
    message = _("Информация о файлах должна быть представлена словарем "
                "с корректными именами файлов в качестве ключей")
    code = "test_files"

    if type(value) != dict:
        raise ValidationError(message, code=code, params={"value": value})

    for key in value.keys():
        validate_file_name(key)
