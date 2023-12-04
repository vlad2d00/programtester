from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from api.db.file_service import create_test_files, delete_test_files, get_tests_names
from api.models import Test


@receiver(post_save, sender=Test)
def test_created_or_updated(sender, **kwargs):
    instance: Test = kwargs['instance']
    create_test_files(test_name=instance.name, test_kits=instance.test_data)

    # Удаление лишних папок
    obj_test_name_list = [obj.name for obj in Test.objects.all()]
    for test_name in get_tests_names():
        if test_name not in obj_test_name_list:
            delete_test_files(test_name=test_name)


@receiver(post_delete, sender=Test)
def test_deleted(sender, **kwargs):
    instance: Test = kwargs['instance']
    delete_test_files(test_name=instance.name)


def signals():
    pass
