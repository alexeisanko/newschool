from datetime import date

from myclass.connecter import MyClassConnecter
from myclass.models import Lesson
from myclass.models import Record
from myclass.models import Teacher


def _load_all_teacher():
    main_params = {
        "method": "get",
        "path": "company/managers",
    }
    connector = MyClassConnecter()
    response = connector.request_to_my_class(
        method=main_params["method"], path=main_params["path"]
    )

    if response:
        for teacher in response:
            defaults = {
                "name": teacher["name"],
                "is_work": teacher["is_work"],
            }
            Teacher.objects.update_or_create(id=teacher["id"], defaults=defaults)


def _load_lessons_by_teacher(date_load: date, teacher_id: int):
    main_params = {
        "method": "get",
        "path": "company/lessons",
    }
    other_params = {
        "date": date_load.strftime("%Y-%m-%d"),
        "includeRecords": True,
        "teacherId": teacher_id,
    }
    connector = MyClassConnecter()
    response = connector.request_to_my_class(
        method=main_params["method"], path=main_params["path"], params=other_params
    )
    if response:
        for lesson in response:
            defaults = {
                "date": date.fromisoformat(lesson["date"]),
                "status": lesson["status"],
                "teacher": Teacher.objects.get(id=teacher_id),
            }
            Lesson.objects.update_or_create(id=lesson["id"], defaults=defaults)
            _save_records(response["records"], lesson["id"])


def _save_records(records: dict, lesson_id: int):
    for record in records:
        defaults = {
            "status": record["status"],
            "student": record["student"],
            "lesson": Lesson.objects.get(id=lesson_id),
            "free": record["free"],
            "visit": record["visit"],
            "good_reason": record["goodReason"],
            "test": record["test"],
            "skip": record["skip"],
            "paid": record["paid"],
        }
        Record.objects.update_or_create(id=record["id"], defaults=defaults)


def update_info_from_myclass(date_load: date):
    _load_all_teacher()
    teachers = Teacher.objects.all()
    for teacher in teachers:
        _load_lessons_by_teacher(date_load, teacher_id=teacher.id)
