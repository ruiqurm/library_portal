import os
import django
from pypinyin import pinyin, lazy_pinyin, Style
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_portal.settings'
django.setup()
from portal.models import *

source = (
    ("期刊", "journal",),
    ("学位论文", "dissertation",),
    ("会议", "conference",),
    ("报纸", "newspaper",),
    ("图书", "book",),
    ("专著", "monograph",),
    ("标准", "standard",),
)
subject = (
    ("综合", "comprehensive",),
    ("数学", "math",),
    ("物理", "physics",),
    ("光学", "optics",),
    ("电气", "electrical",),
    ("电子", "Electronics",),
    ("通信", "telecommunication",),
    ("控制", "control",),
    ("计算机", "computer",),
    ("经济", "economics",),
    ("管理", "administration",),
    ("图书馆", "library",),
    ("情报与档案管理", "information and archives management",),
    ("人文社科", "social science",),
    ("化学", "chemistry",),
    ("生物", "biology",),
    ("语言", "language",),
    ("艺术", "art",),
    ("法律", "law",),
)
category = (
    ("事实型", "fact",),
)
database = (
    "双语智读学术电子图书文库",
    "读览天下阅读平台",
    "3E英语多媒体资源库",
    "ACM数据库",
    "APS（美国物理学会）全文期刊数据库",
    "CNKI中国知网学术平台",
    "CNKI中国精品文化期刊文献库",
    "CSMAR数据库",
    "CSSCI中文社会科学引文索引",
    "Cambridge",
    "EBSCO数据库",
    "EI",
    "Emerald（爱墨瑞得）数据库",
    "Essential",
    "Foundations",
    "Frontiers期刊数据库",
    "HeinOnline法学期刊全文数据库",
    "IEEE-Wiley",
    "IEICE电子刊",
    "IEL(IEEE/IET",
    "IGI",
    "IOP（英国物理学会）全文期刊数据库",
    "ISTP（CPCI-S）（科技会议录索引）数据库",
    "ITU-R标准",
    "ITU-T标准",
    "InCites数据库",
    "Infobank高校财经数据库",
    "JCR",
    "Journal",
    "KUKE库客数字音乐图书馆（消耗校外流量）",
    "Lexis",
    "MeTeL国外高校多媒体教学资源库",
    "Morgan",
    "MyET英语多媒体资源库",
    "NATURE",
    "NoteExpress文献管理软件",
    "OSA（美国光学学会）数据库",
    "PQDT文摘数据库",
    "ProQuest®博硕士论文全文数据库",
    "SCI（科学引文索引）数据库",
    "SIAM数据库",
    "SPIE",
    "SPIE数据库",
    "SSCI（社会科学引文索引）",
    "Science",
    "ScienceDirect数据库",
    "Scientific",
    "Springerlink",
    "VERS维普考试资源系统（消耗校外流量）",
    "Wiley数据库",
    "e-Print",
    "e线图情",
    "“悦学”数据库",
    "“悦读”",
    "万方数字资源",
    "中国光学期刊网数据库",
    "中国引文数据库",
    "中国科学引文数据库(CSCD)",
    "中国科技论文在线",
    "中国通信标准化协会",
    "中科UMajor大学专业课学习数据库（消耗校外流量）",
    "事实数据库",
    "京东阅读电子书阅读室",
    "传奇视频数据库(消耗校外流量)",
    "全球产品样本数据库",
    "全球大学生创新创业与就业升学视频资源平台",
    "其他",
    "创业数字图书馆",
    "北大法宝数据库",
    "句酷批改网",
    "可知电子书平台",
    "台湾学术文献数据库",
    "台湾电子书数据库",
    "国外特种文献发现系统",
    "国家哲学社会科学学术期刊数据库",
    "大雅相似度分析系统",
    "就业数字图书馆",
    "数学文化",
    "新东方在线微课堂学习平台",
    "新东方多媒体学习库（消耗校外流量）",
    "新东方掌学APP",
    "新时代中国特色社会主义思想知识服务平台",
    "橙艺艺术在线",
    "汉斯开源中文期刊",
    "源素通数据库",
    "物理类单订电子期刊",
    "电子图书",
    "维普中文期刊服务平台",
    "英语类单订电子期刊",
    "计算机类单订电子期刊",
    "超星期刊",
    "超星电子图书数据",
    "超星镜像电子书",
    "软件通",
    "通信产业竞争情报监测报告",
)
import datetime
from pytz import timezone
cst_tz = timezone('Asia/Shanghai')
def random_date(begin: datetime.datetime, end: datetime.datetime):
    epoch = datetime.datetime(1970, 1, 1)
    begin_seconds = int((begin - epoch).total_seconds())
    end_seconds = int((end - epoch).total_seconds())
    dt_seconds = random.randint(begin_seconds, end_seconds)

    return datetime.datetime.fromtimestamp(dt_seconds).replace(tzinfo=cst_tz)

if not MyUser.objects.filter(username="temp").exists():
    MyUser.objects.create_user("temp")
user = MyUser.objects.get(username="temp")

# DatabaseSubject
DatabaseSubject.objects.all().delete()
DatabaseSubject.objects.bulk_create(
    [DatabaseSubject(cn_name=cn,en_name=en) for cn,en in subject]
)

# DatabaseSource
DatabaseSource.objects.all().delete()
DatabaseSource.objects.bulk_create(
    [DatabaseSource(cn_name=cn,en_name=en) for cn,en in source]
)

DatabaseCategory.objects.all().delete()
DatabaseCategory.objects.bulk_create(
    [DatabaseCategory(cn_name=cn,en_name=en) for cn,en in category]
)

"""
插入数据库数据
"""
subject_ids = [obj.id for obj in DatabaseSubject.objects.all()]
source_ids = [obj.id for obj in DatabaseSource.objects.all()]
category_ids = [obj.id for obj in DatabaseCategory.objects.all()]
Database.objects.all().delete()
import random
import datetime
import tqdm
save_result = []
name_to_subject = {}
for name in tqdm.tqdm(database):
    cn_name = name
    en_name = " ".join(lazy_pinyin(name))
    category_id =  random.choice(category_ids)
    source_id = random.choice(source_ids)
    subjectids = random.sample(subject_ids,random.randint(1, 5))
    is_chinse = random.choice([True, False])
    is_on_trial = random.choice([True, False])
    on_trial = random_date(datetime.datetime.today(),datetime.datetime.now()+datetime.timedelta(days=365*2)) if is_on_trial else None
    d = Database(cn_name=cn_name,en_name=en_name,category_id=category_id,source_id=source_id,publisher=user,
             is_Chinese=is_chinse,is_on_trial=is_on_trial,on_trial=on_trial,cn_content=cn_name,en_content=en_name,is_available=True)
    name_to_subject[cn_name] = subjectids
    save_result.append(d)
Database.objects.bulk_create(
    save_result
)
ThroughModel = Database.subject.through
subject_middle_result = []
for i in save_result:
    for j in name_to_subject[i.cn_name]:
        subject_middle_result.append(ThroughModel(database_id=i.id,databasesubject_id=j))
ThroughModel.objects.bulk_create(
    subject_middle_result
)


database_ids = [obj.id for obj in Database.objects.all()]

common_announcement_content = """
   因疫情防控考虑到部分学生未返校，为了方便读者继续借阅图书，图书外借期限调整如下：
       1、自2021年12月27日起到2022年3月1日，外借期限为30天的借阅证外借期限临时调整为95天，寒假开学后恢复为30天。
       2、还书日期在2022年1月1日—3月15日的寒假到期图书，还书日期统一调整为2022年4月20日。
       3、图书馆会对寒假期间到期的图书进行延迟还书调整，确保读者在寒假期间无需续借或还书。
图书馆
2021年3月19日
"""
common_announcement_content_en = """
Due to the epidemic prevention and control, considering that some students have not returned to school, in order to facilitate readers to continue to borrow books, the loan period of books is adjusted as follows:
1. From December 27, 2021 to March 1, 2022, the lending period of the borrowing card with a lending period of 30 days will be temporarily adjusted to 95 days, and will be restored to 30 days after the winter vacation.
2. For books due during the winter vacation from January 1 to March 15, 2022, the return date is uniformly adjusted to April 20, 2022.
3. The library will adjust the delayed return of books due during the winter vacation to ensure that readers do not need to renew or return books during the winter vacation.
library
March 19, 2021
"""
save_result = []
for i in tqdm.tqdm(range(100)):
    connect_to_database = random.randint(0,7)<=1
    database_key = random.choice(database_ids) if connect_to_database else None
    save_result.append(Announcement(
        cn_title = f"公告{i}",
        en_title = f"announcement{i}",
        publisher= user,
        cn_content= common_announcement_content,
        en_content=common_announcement_content_en,
        database_id = database_key,
        is_available=True
    ))
Announcement.objects.bulk_create(
    save_result
)

print("添加完成")