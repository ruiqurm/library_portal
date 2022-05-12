import os
import django
from pypinyin import lazy_pinyin
# print(os.getcwd())
# os.environ['PYTHONPATH']= r"F:\program\library_portal"
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_portal.settings'

django.setup()
from portal.models import *

import csv

MyUser.objects.all().delete()
DatabaseCategory.objects.all().delete()
DatabaseSource.objects.all().delete()
DatabaseSubject.objects.all().delete()
Database.objects.all().delete()
"""
Read User
"""
users = dict()
with open("./data/user.csv")as f:
    reader = csv.reader(f)
    header_row = next(reader)
    for i in reader:
        assert  len(i) ==4
        users[i[1]] = MyUser(username=i[1],password=i[2],is_active=True,is_staff=True,is_superuser=True)

MyUser.objects.bulk_create([users[key] for key in users.keys()])
users["test"] = MyUser.objects.create_superuser(username="test",email="",password="test")
"""
Read source,subject,category
"""
# source = dict()
# with open("./data/databasesource.csv")as f:
#     reader = csv.reader(f)
#     header_row = next(reader)
#     for i in reader:
#         source[i[1]] = DatabaseSource(i[1])
# DatabaseSource.objects.bulk_create([source[key] for key in source.keys()])
#
# category =dict()
# with open("./data/databasecategory.csv")as f:
#     reader = csv.reader(f)
#     header_row = next(reader)
#     for i in reader:
#         category[i[1]] = DatabaseCategory(i[1])
# DatabaseCategory.objects.bulk_create([category[key] for key in category.keys()])
#
# subject = dict()
# with open("./data/databasesubject.csv")as f:
#     reader = csv.reader(f)
#     header_row = next(reader)
#     for i in reader:
#         subject[i[1]] = DatabaseSubject(i[1])
# DatabaseSubject.objects.bulk_create([subject[key] for key in subject.keys()])

source = dict()
subject = dict()
category = dict()
def create_or_get(d,name):
    if d is source:# str
        if name not in source:
            source[name] = DatabaseSource.objects.create(name=name)
        return source[name]
    elif d is subject:# list
        l = []
        for n in name:
            if n not in subject:
                subject[n] = DatabaseSubject.objects.create(name=n)
            l.append(subject[n])
        return l
    elif d is category:# str
        if name not in category:
            category[name] = DatabaseCategory.objects.create(name=name)
        return category[name]
    elif d is users:# str
        if name in d:
            return d[name]
        else:
            raise
    else:
        raise

"""
Database
"""
database = dict()
subject_of_database = dict()
with open("./data/database.csv")as f:
    reader = csv.reader(f)
    header_row = next(reader)
    for i in reader:
        cat = create_or_get(category,i[2].split("/")[0])
        src = create_or_get(source,i[3])
        sub = create_or_get(subject,list(map(str.strip,i[4].split("/"))))
        usr = create_or_get(users,i[7])

        database[i[1]] = Database(name=i[1],category=cat,source=src,publisher=usr,
                                  is_Chinese=eval(i[8].title()),is_available=eval(i[9].title()),is_on_trial=eval(i[10].title()))
        subject_of_database[i[1]] = sub
Database.objects.bulk_create([database[key] for key in database.keys()])

ThroughModel = Database.subject.through
subject_middle_result = []
for key in database:
    i = database[key]
    for j in subject_of_database[i.name]:
        subject_middle_result.append(ThroughModel(database=i, databasesubject=j))
ThroughModel.objects.bulk_create(
    subject_middle_result
)
"""
Announcement
"""
announcement = []
with open("./data/announcement.csv")as f:
    reader = csv.reader(f)
    header_row = next(reader)
    for i in reader:
        t = Announcement(
            title=i[1],
            publisher=create_or_get(users,i[4]),
            content=i[5],
            is_available=eval(i[7].title())
        )
        announcement.append(t)
Announcement.objects.all().delete()
Announcement.objects.bulk_create(announcement)