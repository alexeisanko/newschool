import pandas as pd
from newschool.myclass.connecter import MyClassConnecter
from django.conf import settings

def calculate_statistic_teacher(date):
    params = {"date": date,
            "includeRecords": 'true',
            "limit": 500,
            "offset": 0}

    myclass = MyClassConnecter()
    lessons = myclass.request_to_my_class("GET", "company/lessons", params)
    print(lessons)
    teachers = myclass.request_to_my_class("GET", "company/managers")
    df_lessons = pd.DataFrame.from_dict(lessons["lessons"])
    df_lessons = df_lessons.explode("teacherIds")
    df_lessons = df_lessons.drop(
        [
            "filialId",
            "roomId",
            "classId",
            "comment",
            "maxStudents",
            "topic",
            "description",
            "date",
            "beginTime",
            "endTime",
            "createdAt",
        ],
        axis=1,
    )
    df_lessons = df_lessons.rename(columns={"teacherIds": "teacherId", "id": "lessonId"})


    count_lessons_by_teacher = df_lessons.groupby(by=["teacherId"], as_index=False).count()[["teacherId", "lessonId", "status"]]
    count_lessons_by_teacher = count_lessons_by_teacher.rename(columns={"lessonId": "planLessons", "status": "factLessons"})
    count_lessons_by_teacher = count_lessons_by_teacher.set_index('teacherId')

    df_lessons  =df_lessons.drop(["status"], axis=1)
    df_records = df_lessons["records"]
    df_lessons = df_lessons.drop(["records"], axis=1)

    df_records = df_records.explode("records")
    df_records = pd.DataFrame(df_records.tolist())[["free", "visit", "goodReason", "test", "paid", "lessonId"]]

    records_data = df_records.groupby("lessonId").sum()
    records_data["isIndividualLessons"] = records_data["paid"] + records_data["free"] + records_data["goodReason"] == 1
    records_data["isTwinLessons"] = records_data["paid"] + records_data["free"] + records_data["goodReason"] == 2
    records_data["isGroupLessons"] = records_data["paid"] + records_data["free"] + records_data["goodReason"] > 2

    df_teacher = pd.DataFrame.from_dict(teachers)[["id", "name"]]
    df_teacher = df_teacher.rename(columns={"id": "teacherId", "name": "teacherName"}).set_index('teacherId')

    clean_data = df_lessons.join(records_data, on="lessonId")
    clean_data = clean_data.groupby("teacherId", as_index=False).sum().drop(["lessonId"], axis=1)
    clean_data = clean_data.join(df_teacher, "teacherId")
    clean_data = clean_data.join(count_lessons_by_teacher, "teacherId").drop(["teacherId"], axis=1)
    clean_data["planVisit"] = clean_data["paid"] + clean_data["goodReason"] + clean_data["free"]
    clean_data["badReason"] = clean_data["paid"] - clean_data["visit"] + clean_data["free"]
    clean_data = clean_data[clean_data.columns[[8, 9, 10, 5, 6, 7, 11, 1, 4, 0, 3, 2, 12]]]

    translate_columns = {
        "teacherName": "ФИО репетитора",
        "planLessons": "Количество занятий план",
        "factLessons": "Количество занятий факт",
        "isIndividualLessons": "Количество индивидуальных занятий факт",
        "isTwinLessons": "Количество парных занятий факт",
        "isGroupLessons": "Количество групповых занятий факт",
        "planVisit": "количество посещений всего план",
        "visit": "количество посещений всего факт",
        "free": "количество бесплатных посещений (включая пробные занятия)",
        "test": "количество пробных посещений факт",
        "goodReason": "Отсутствие по ув. причине",
        "badReason": "Отсутствие по не ув. причине",
        "paid": "количество оплачиваемых посещений(включая пропущенные по не ув. причине)",
    }
    clean_data = clean_data.rename(columns=translate_columns)
    return clean_data.to_dict(orient='records')