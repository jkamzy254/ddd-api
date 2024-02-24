from rest_framework import serializers
from ddd.models import Memberdata, Bbdata, Evseason, Report
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model=Memberdata
        fields=["id","name","membergroup", "region", "group_imwy", "internal_position", "bbt", "uid"]
        