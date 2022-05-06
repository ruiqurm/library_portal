from typing import Union
from .models import DatabaseCategory,DatabaseSubject,DatabaseSource,AnnouncementTag
def get_by_id_if_exists_and_serialize(cls,serializer,value)->Union[dict,None,list[dict]]:
    if not value:
        return
    if isinstance(value,int):
        try:
            return serializer(cls.objects.get(id=value)).data
        except cls.DoesNotExist:
            return None
    elif isinstance(value,list):
        q = cls.objects.filter(id__in=value)
        if q.exists():
            return serializer(q.all(),many=True).data
        else:
            return None