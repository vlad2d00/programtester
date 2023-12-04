from django.contrib.auth.models import User

from api.db.config import ProgramLangName
from api.models import ProgramLang


def init_db():
    if not User.objects.filter(is_superuser=True):
        User.objects.create_superuser(username='admin', password='admin',
                                      first_name='Админ', last_name='Админович')

    program_language_name_list = [x.name for x in ProgramLang.objects.all()]
    for value in [x.value for x in ProgramLangName]:
        if value not in program_language_name_list:
            ProgramLang.objects.create(name=value)
