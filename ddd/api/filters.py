from django_filters.rest_framework import FilterSet
from ddd.models import Memberdata, Report, Bbdata, Evseason

class MemberFilter(FilterSet):
    class Meta:
        model = Memberdata
        fields = {
            'membergroup': ['exact'],
            'id': ['gt','lt']
        }

class BBDataFilter(FilterSet):
    class Meta:
        model = Bbdata
        fields = {
            'status': ['exact'],
            'stat_abbr': ['exact'],
            'season': ['gt','lt']
        }

class SeasonFilter(FilterSet):
    class Meta:
        model = Evseason
        fields = {
            'id': ['exact'],
            'startdate': ['gt','lt'],
            'enddate': ['gt','lt']
        }

class ReportFilter(FilterSet):
    class Meta:
        model = Report
        fields = {
            'reportid': ['exact'],
            'topic': ['exact'],
            'classdate': ['gt','lt']
        }