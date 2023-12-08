from rest_framework import serializers
from ddd.models import Memberdata, Bbdata, Evseason, Report, ProImage
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model=Memberdata
        fields=["id","name","membergroup", "region", "group_imwy", "internal_position", "bbt", "uid"]
        
# class MemberForBBTSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Memberdata
#         fields=["id","name","membergroup", "region", "group_imwy", "internal_position", "bbt", "uid"]

class EvseasonSerializer(serializers.ModelSerializer):
    class Meta:
        model=Evseason
        fields=["id","seasonname","startdate","enddate","closingdate","region","dept"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProImage
        fields=["id","seasonname","startdate","enddate","closingdate","region","dept"]

class LeafSerializer(serializers.ModelSerializer):
    class Meta:
        model=Memberdata
        fields=["uid","name","membergroup"]

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model=Report
        fields=["reportid","classdate","topic","attendee_1", "attendee_2", "label"]
        
    attendee_1 = LeafSerializer()
    attendee_2 = LeafSerializer()
    
    def create(self, validated_data):
        bbid = self.context["uid"]
        return super().create(validated_data)
        
    # uid = BBDataSerializer()
    # attendee_1 = MemberSerializer()
    # attendee_2 = MemberSerializer()

class BBGroupSerializer(serializers.ModelSerializer):
    class Meta:
        # model=Report
        fields=['UID', 'LastClass', 'L1P', 'L2P', 'L1_Name', 'L2_Name', 'M1G', 'M2G', 'BBT_Name', 'Stage', 'FishName', 'Stage_P', 'Stage_M', 'Stage_F', 'BB_Status', 'LastUpdate', 'StAbbr', 'Points']
        
    # attendee_1 = LeafSerializer()
    # attendee_2 = LeafSerializer()
    
    # def create(self, validated_data):
    #     bbid = self.context["uid"]
    #     return super().create(validated_data)

class BBDataSerializer(serializers.ModelSerializer):
    rep = ReportSerializer(many=True)
    class Meta:
        model=Bbdata
        fields=["fruitname","status","stat_abbr","lastupdate","bbid", "season", "l1_id", "l2_id","rep"]
        # fields=["uid","status","stat_abbr","lastupdate","bbid", "season", "l1_id", "l2_id", "bbt_id", "reports"]
        
    # season = serializers.StringRelatedField()
    # l1_id = serializers.StringRelatedField()
    # l2_id = serializers.StringRelatedField()
    # bbt_id = MemberSerializer()