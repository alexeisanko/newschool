from celery import shared_task

from newschool.myclass.utils import update_student_from_db


@shared_task()
def load_student_info():
    update_student_from_db()
