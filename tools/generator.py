from faker import Faker
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'library_portal.settings'
django.setup()
from portal.models import *


print(Announcement.objects.all())