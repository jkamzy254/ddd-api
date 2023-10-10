# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class AutoUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 5
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        del kwargs['unique']
        return name, path, args, kwargs

    def increment_id(self, current_id):
        # This function increments the custom ID according to the specified pattern.
        if current_id == 'ZZZZZ':
            return '00000'

        current_num = int(current_id, 36)  # Convert to base 36
        current_num += 1
        new_id = base36encode(current_num).zfill(6)
        return new_id

def base36encode(number):
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")
    if number < 0:
        raise ValueError("Input must be non-negative")

    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36 = ''

    while number > 0:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36


# class Attendancedata(models.Model):
#     attendanceid = models.AutoField(db_column='AttendanceID')  # Field name made lowercase.
#     memberid = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='MemberID', max_length=50, blank=True, null=True, related_name='uid')  # Field name made lowercase.
#     expected = models.TextField(db_column='Expected', blank=True, null=True)  # Field name made lowercase.
#     expectedreason = models.TextField(db_column='ExpectedReason', blank=True, null=True)  # Field name made lowercase.
#     attended = models.TextField(db_column='Attended', blank=True, null=True)  # Field name made lowercase.
#     attendedreason = models.TextField(db_column='AttendedReason', blank=True, null=True)  # Field name made lowercase.
#     tardy = models.BooleanField(db_column='Tardy', blank=True, null=True)  # Field name made lowercase.
#     tardyreason = models.TextField(db_column='TardyReason', blank=True, null=True)  # Field name made lowercase.
#     notes = models.BooleanField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
#     serviceid = models.IntegerField(db_column='ServiceID', blank=True, null=True)  # Field name made lowercase.
#     attendedtime = models.DateTimeField(db_column='AttendedTime', blank=True, null=True)  # Field name made lowercase.
#     expectedtime = models.DateTimeField(db_column='ExpectedTime', blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'AttendanceData'
        
        
class Bbdata(models.Model):
    bbid = models.AutoField(db_column='BBID', primary_key=True)  # Field name made lowercase.
    fruitkey = models.IntegerField(db_column='FruitKey', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50)  # Field name made lowercase.
    created = models.DateTimeField(db_column='Created', blank=True, null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpdate', blank=True, null=True)  # Field name made lowercase.
    fruitname = models.CharField(db_column='FruitName', max_length=50)  # Field name made lowercase.
    l1_id = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='L1_ID', max_length=50, blank=True, null=True, to_field='uid', related_name='bbdata_l1_uid')  # Field name made lowercase.
    l2_id = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='L2_ID', max_length=50, blank=True, null=True, to_field='uid', related_name='bbdata_l2_uid')  # Field name made lowercase.
    bbt_id = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='BBT_ID', max_length=50, blank=True, null=True, to_field='uid', related_name='bbdata_bbt_uid')  # Field name made lowercase.
    completed = models.BooleanField(db_column='Completed', blank=True, null=True)  # Field name made lowercase.
    last_topic = models.TextField(db_column='Last_Topic', blank=True, null=True)  # Field name made lowercase.
    stat_abbr = models.CharField(db_column='Stat_Abbr', max_length=50, blank=True, null=True)  # Field name made lowercase.
    label = models.CharField(db_column='Label', max_length=50, blank=True, null=True)  # Field name made lowercase.
    l2points = models.FloatField(db_column='L2Points', blank=True, null=True)  # Field name made lowercase.
    l1points = models.FloatField(db_column='L1Points', blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # uid = models.ForeignKey('Fruitdata', on_delete=models.DO_NOTHING, db_column='UID', max_length=50, to_field='uid', unique=True)  # Field name made lowercase.
    uid = models.OneToOneField('Fruitdata', on_delete=models.DO_NOTHING, db_column='UID', to_field='uid')  # Field name made lowercase.
    # uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    season = models.ForeignKey('Evseason', on_delete=models.DO_NOTHING,db_column='Season', blank=True, null=True, to_field='id')  # Field name made lowercase.
    nextclassdate = models.DateTimeField(db_column='NextClassDate', blank=True, null=True)  # Field name made lowercase.
    
    
    # def __str__(self):
    #     return self.fruitname if self.fruitname else ''

    class Meta:
        managed = False
        db_table = 'BBData'


class Bblogs(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    logdate = models.DateTimeField(db_column='LogDate')  # Field name made lowercase.
    student = models.ForeignKey('Fruitdata', on_delete=models.DO_NOTHING,db_column='Student', max_length=50, blank=True, null=True, to_field='uid')  # Field name made lowercase.
    bbt = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='BBT', max_length=50, blank=True, null=True, to_field='uid')  # Field name made lowercase.
    logcategory = models.CharField(db_column='LogCategory', max_length=50, blank=True, null=True)  # Field name made lowercase.
    studstatus = models.CharField(db_column='StudStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    logtype = models.CharField(db_column='LogType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    opened = models.BooleanField(db_column='Opened', blank=True, null=True)  # Field name made lowercase.
    readby = models.TextField(db_column='ReadBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBLogs'


class Bbstatusdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    stat_abbr = models.CharField(db_column='Stat_Abbr', max_length=50, blank=True, null=True)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBStatusData'


# class Bbt(models.Model):
#     id = models.SmallIntegerField(db_column='ID', blank=True, null=True)  # Field name made lowercase.
#     status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'BBT'


class Bbtlog(models.Model):
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    btmno = models.CharField(db_column='BtmNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBTLog'


class Bbteacherdata(models.Model):
    bbtid = models.CharField(db_column='BBTID', primary_key=True, max_length=50)  # Field name made lowercase.
    btm = models.CharField(db_column='BTM', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bbtstatus = models.CharField(db_column='BBTStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    feedbackbbt = models.CharField(db_column='FeedBackBBT', max_length=255, blank=True, null=True)  # Field name made lowercase.
    feedbackbbtid = models.CharField(db_column='FeedBackBBTID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBTeacherData'


class Bbtopicdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.
    label = models.CharField(db_column='Label', max_length=100, blank=True, null=True)  # Field name made lowercase.
    short = models.CharField(db_column='Short', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBTopicData'


class Bbweeklysum(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    weekno = models.CharField(db_column='WeekNo', max_length=255)  # Field name made lowercase.
    weekstart = models.DateTimeField(db_column='WeekStart', blank=True, null=True)  # Field name made lowercase.
    weekend = models.DateTimeField(db_column='WeekEnd', blank=True, null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpdate', blank=True, null=True)  # Field name made lowercase.
    p = models.FloatField(db_column='P', blank=True, null=True)  # Field name made lowercase.
    fe = models.FloatField(db_column='FE', blank=True, null=True)  # Field name made lowercase.
    ong = models.FloatField(db_column='ONG', blank=True, null=True)  # Field name made lowercase.
    stb = models.FloatField(db_column='STB', blank=True, null=True)  # Field name made lowercase.
    ct = models.FloatField(db_column='CT', blank=True, null=True)  # Field name made lowercase.
    cct = models.FloatField(db_column='CCT', blank=True, null=True)  # Field name made lowercase.
    me = models.FloatField(db_column='ME', blank=True, null=True)  # Field name made lowercase.
    nct = models.FloatField(db_column='NCT', blank=True, null=True)  # Field name made lowercase.
    fa = models.FloatField(db_column='FA', blank=True, null=True)  # Field name made lowercase.
    active = models.FloatField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    inactive = models.FloatField(db_column='Inactive', blank=True, null=True)  # Field name made lowercase.
    total = models.FloatField(db_column='Total', blank=True, null=True)  # Field name made lowercase.
    region = models.TextField(db_column='Region', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BBWeeklySum'


class Bondingdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.ForeignKey('Fruitdata', on_delete=models.DO_NOTHING, db_column='UID', max_length=50, to_field='uid')  # Field name made lowercase.
    bbt = models.CharField(db_column='BBT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bondlocation = models.CharField(db_column='BondLocation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bondduration = models.CharField(db_column='BondDuration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attendees = models.CharField(db_column='Attendees', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bondtype = models.CharField(db_column='BondType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    verseshared = models.CharField(db_column='VerseShared', max_length=50, blank=True, null=True)  # Field name made lowercase.
    willingtomeet = models.CharField(db_column='WillingToMeet', max_length=50, blank=True, null=True)  # Field name made lowercase.
    purpose = models.TextField(db_column='Purpose', blank=True, null=True)  # Field name made lowercase.
    bonddate = models.DateField(db_column='BondDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BondingData'


class Ctcarddata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.ForeignKey('Bbdata', on_delete=models.DO_NOTHING, db_column='UID', max_length=50, to_field='uid')  # Field name made lowercase.
    l1_concept_p = models.TextField(db_column='L1_Concept_P', blank=True, null=True)  # Field name made lowercase.
    l2_concept_p = models.TextField(db_column='L2_Concept_P', blank=True, null=True)  # Field name made lowercase.
    bbt_concept = models.TextField(db_column='BBT_Concept', blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=50, blank=True, null=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='First_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    middle_name = models.CharField(db_column='Middle_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=50, blank=True, null=True)  # Field name made lowercase.
    birthday = models.DateField(db_column='Birthday', blank=True, null=True)  # Field name made lowercase.
    marital_status = models.CharField(db_column='Marital_Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hobby = models.TextField(db_column='Hobby', blank=True, null=True)  # Field name made lowercase.
    first_language = models.CharField(db_column='First_Language', max_length=255, blank=True, null=True)  # Field name made lowercase.
    first_language_proficiency = models.CharField(db_column='First_Language_Proficiency', max_length=50, blank=True, null=True)  # Field name made lowercase.
    second_language = models.CharField(db_column='Second_Language', max_length=255, blank=True, null=True)  # Field name made lowercase.
    second_language_proficiency = models.CharField(db_column='Second_Language_Proficiency', max_length=50, blank=True, null=True)  # Field name made lowercase.
    birth_city = models.CharField(db_column='Birth_City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    birth_country = models.CharField(db_column='Birth_Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nationality = models.CharField(db_column='Nationality', max_length=50, blank=True, null=True)  # Field name made lowercase.
    occupation = models.CharField(db_column='Occupation', max_length=255, blank=True, null=True)  # Field name made lowercase.
    occupation_address = models.TextField(db_column='Occupation_Address', blank=True, null=True)  # Field name made lowercase.
    financial_stabiliy = models.CharField(db_column='Financial_Stabiliy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    occupation_travel_time = models.CharField(db_column='Occupation_Travel_Time', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_studying = models.CharField(db_column='Is_Studying', max_length=50, blank=True, null=True)  # Field name made lowercase.
    education_institute = models.CharField(db_column='Education_Institute', max_length=255, blank=True, null=True)  # Field name made lowercase.
    course = models.CharField(db_column='Course', max_length=255, blank=True, null=True)  # Field name made lowercase.
    school_travel_time = models.CharField(db_column='School_Travel_Time', max_length=50, blank=True, null=True)  # Field name made lowercase.
    year_since_lof = models.CharField(db_column='Year_Since_LOF', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attending_church = models.CharField(db_column='Attending_Church', max_length=50, blank=True, null=True)  # Field name made lowercase.
    church_name = models.CharField(db_column='Church_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    denomination = models.CharField(db_column='Denomination', max_length=255, blank=True, null=True)  # Field name made lowercase.
    church_position = models.CharField(db_column='Church_Position', max_length=255, blank=True, null=True)  # Field name made lowercase.
    church_address = models.TextField(db_column='Church_Address', blank=True, null=True)  # Field name made lowercase.
    babylon_bible_study = models.CharField(db_column='Babylon_Bible_Study', max_length=50, blank=True, null=True)  # Field name made lowercase.
    family_info = models.TextField(db_column='Family_Info', blank=True, null=True)  # Field name made lowercase.
    good_qualities = models.TextField(db_column='Good_Qualities', blank=True, null=True)  # Field name made lowercase.
    bad_qualities = models.TextField(db_column='Bad_Qualities', blank=True, null=True)  # Field name made lowercase.
    how_evangelized = models.TextField(db_column='How_Evangelized', blank=True, null=True)  # Field name made lowercase.
    fm_to_ct = models.TextField(db_column='FM_To_CT', blank=True, null=True)  # Field name made lowercase.
    bbt_concerns = models.TextField(db_column='BBT_Concerns', blank=True, null=True)  # Field name made lowercase.
    bb_reaction = models.TextField(db_column='BB_Reaction', blank=True, null=True)  # Field name made lowercase.
    sealingmouth_done = models.CharField(db_column='SealingMouth_Done', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sealingmouth_reaction = models.TextField(db_column='SealingMouth_Reaction', blank=True, null=True)  # Field name made lowercase.
    has_alibi = models.CharField(db_column='Has_Alibi', max_length=50, blank=True, null=True)  # Field name made lowercase.
    alibi_desc = models.TextField(db_column='Alibi_Desc', blank=True, null=True)  # Field name made lowercase.
    student_obstacles = models.TextField(db_column='Student_Obstacles', blank=True, null=True)  # Field name made lowercase.
    plan_to_overcome = models.TextField(db_column='Plan_To_Overcome', blank=True, null=True)  # Field name made lowercase.
    english_proficiency = models.CharField(db_column='English_Proficiency', max_length=50, blank=True, null=True)  # Field name made lowercase.
    scj_biblestudy = models.CharField(db_column='SCJ_BibleStudy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    romance = models.CharField(db_column='Romance', max_length=50, blank=True, null=True)  # Field name made lowercase.
    romance_duration = models.CharField(db_column='Romance_Duration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    travel_plan = models.CharField(db_column='Travel_Plan', max_length=50, blank=True, null=True)  # Field name made lowercase.
    travel_plan_duration = models.CharField(db_column='Travel_Plan_Duration', max_length=255, blank=True, null=True)  # Field name made lowercase.
    medical = models.CharField(db_column='Medical', max_length=50, blank=True, null=True)  # Field name made lowercase.
    medical_desc = models.TextField(db_column='Medical_Desc', blank=True, null=True)  # Field name made lowercase.
    know_scj = models.CharField(db_column='Know_SCJ', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ct_days = models.CharField(db_column='CT_Days', max_length=50, blank=True, null=True)  # Field name made lowercase.
    stable_internet = models.CharField(db_column='Stable_Internet', max_length=50, blank=True, null=True)  # Field name made lowercase.
    internet_access = models.CharField(db_column='Internet_Access', max_length=50, blank=True, null=True)  # Field name made lowercase.
    devices = models.TextField(db_column='Devices', blank=True, null=True)  # Field name made lowercase.
    photo_link = models.TextField(db_column='Photo_Link', blank=True, null=True)  # Field name made lowercase.
    l1_concept_s = models.TextField(db_column='L1_Concept_S', blank=True, null=True)  # Field name made lowercase.
    l2_concept_s = models.TextField(db_column='L2_Concept_S', blank=True, null=True)  # Field name made lowercase.
    photoname = models.TextField(db_column='PhotoName', blank=True, null=True)  # Field name made lowercase.
    address = models.TextField(db_column='Address', blank=True, null=True)  # Field name made lowercase.
    visa = models.CharField(db_column='Visa', max_length=255, blank=True, null=True)  # Field name made lowercase.
    visaremain = models.CharField(db_column='VisaRemain', max_length=255, blank=True, null=True)  # Field name made lowercase.
    visaplan = models.CharField(db_column='VisaPlan', max_length=255, blank=True, null=True)  # Field name made lowercase.
    spirituality = models.IntegerField(db_column='Spirituality', blank=True, null=True)  # Field name made lowercase.
    primaryphone = models.BigIntegerField(db_column='PrimaryPhone', blank=True, null=True)  # Field name made lowercase.
    has_occupation = models.CharField(db_column='Has_Occupation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cansubmit = models.CharField(db_column='CanSubmit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    home_travel_time = models.CharField(db_column='Home_Travel_Time', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cardstatus = models.CharField(db_column='CardStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=50, blank=True, null=True)  # Field name made lowercase.
    studstate = models.CharField(db_column='StudState', max_length=50, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    postcode = models.CharField(db_column='Postcode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    timestamp = models.CharField(db_column='Timestamp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    profpicid = models.CharField(db_column='ProfPicID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CTCardData'


class Ctdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='FIRST_NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    middle_name = models.CharField(db_column='MIDDLE_NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='LAST_NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    preferred_name = models.CharField(db_column='PREFERRED_NAME', max_length=255, blank=True, null=True)  # Field name made lowercase.
    jdsn = models.IntegerField(db_column='JDSN', blank=True, null=True)  # Field name made lowercase.
    ctnum = models.CharField(db_column='CTNum', max_length=50, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    latestregistration = models.CharField(db_column='LatestRegistration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    homeroom = models.CharField(db_column='Homeroom', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone = models.CharField(db_column='Phone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone2 = models.BigIntegerField(db_column='Phone2', blank=True, null=True)  # Field name made lowercase.
    facebook = models.CharField(db_column='Facebook', max_length=50, blank=True, null=True)  # Field name made lowercase.
    instagram = models.CharField(db_column='Instagram', max_length=50, blank=True, null=True)  # Field name made lowercase.
    registeredjdsn = models.IntegerField(db_column='RegisteredJDSN', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CTData'


class Ctdatachangelog(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    jdsn = models.IntegerField(db_column='JDSN', blank=True, null=True)  # Field name made lowercase.
    ctnum = models.CharField(db_column='CTNum', max_length=50, blank=True, null=True)  # Field name made lowercase.
    latestregistration = models.TextField(db_column='LatestRegistration', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updatedate = models.CharField(db_column='UpdateDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    edittype = models.CharField(db_column='EditType', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CTDataChangeLog'


class Codeyfunctionlogs(models.Model):
    uid = models.CharField(db_column='UID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    commandsent = models.CharField(db_column='CommandSent', max_length=255, blank=True, null=True)  # Field name made lowercase.
    functionname = models.CharField(db_column='FunctionName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tstamp = models.DateTimeField(db_column='TStamp', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CodeyFunctionLogs'
        

class Ctcatdlogdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    cardid = models.ForeignKey(Ctcarddata, models.DO_NOTHING, db_column='CardId', blank=True, null=True)  # Field name made lowercase.
    writedate = models.CharField(db_column='WriteDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    modifydate = models.CharField(db_column='ModifyDate', max_length=50, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CtCatdLogData'


class Deletefishdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=255, blank=True, null=True)  # Field name made lowercase.
    reportedby = models.CharField(db_column='ReportedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DeleteFishData'


class Deptdata(models.Model):
    did = models.AutoField(db_column='DID', primary_key=True)  # Field name made lowercase.
    department = models.CharField(db_column='Department', max_length=255)  # Field name made lowercase.
    rid = models.IntegerField(db_column='RID', blank=True, null=True)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.
    abbr = models.CharField(db_column='Abbr', max_length=10, blank=True, null=True)  # Field name made lowercase.
    deptleader = models.CharField(db_column='DeptLeader', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DeptData'


class Evactivity(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    activityname = models.CharField(db_column='ActivityName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    activityweek = models.IntegerField(db_column='ActivityWeek', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    weekgoal = models.FloatField(db_column='WeekGoal', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EVActivity'


class Evdaylocationdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    evdayid = models.IntegerField(db_column='EVDayID', blank=True, null=True)  # Field name made lowercase.
    group = models.CharField(db_column='Group', max_length=50, blank=True, null=True)  # Field name made lowercase.
    locationid = models.CharField(db_column='LocationID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EVDayLocationData'


class Evseason(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    seasonname = models.CharField(db_column='SeasonName', max_length=255)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    region = models.TextField(db_column='Region', blank=True, null=True)  # Field name made lowercase.
    pickinggoal = models.IntegerField(db_column='PickingGoal', blank=True, null=True)  # Field name made lowercase.
    ctgoal = models.IntegerField(db_column='CTGoal', blank=True, null=True)  # Field name made lowercase.
    closingdate = models.DateTimeField(db_column='ClosingDate', blank=True, null=True)  # Field name made lowercase.
    dept = models.CharField(db_column='Dept', max_length=50, blank=True, null=True)  # Field name made lowercase.
    
    def __str__(self):
        return self.seasonname

    class Meta:
        managed = False
        db_table = 'EVSeason'


class Enquiries(models.Model):
    eid = models.AutoField(db_column='EID', primary_key=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)  # Field name made lowercase.
    enq_description = models.TextField(db_column='Enq_Description', blank=True, null=True)  # Field name made lowercase.
    resolved = models.BooleanField(db_column='Resolved', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Enquiries'


class Explogdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    meettype = models.CharField(db_column='MeetType', max_length=10, blank=True, null=True)  # Field name made lowercase.
    meetdate = models.DateField(db_column='MeetDate', blank=True, null=True)  # Field name made lowercase.
    reschedule = models.CharField(db_column='Reschedule', max_length=10, blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    recorder = models.CharField(db_column='Recorder', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ExpLogData'


class Expnotmet(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    expdate = models.DateTimeField(db_column='ExpDate', blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=255, blank=True, null=True)  # Field name made lowercase.
    rescheduled = models.CharField(db_column='Rescheduled', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nextdate = models.DateTimeField(db_column='NextDate', blank=True, null=True)  # Field name made lowercase.
    recordedby = models.CharField(db_column='RecordedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ExpNotMet'


class Fallendata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fruitkey = models.IntegerField(db_column='FruitKey', blank=True, null=True)  # Field name made lowercase.
    bbtid = models.CharField(db_column='BBTID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    allreasons = models.TextField(db_column='AllReasons', blank=True, null=True)  # Field name made lowercase.
    sfaenvmain = models.TextField(db_column='sFaEnvMain', blank=True, null=True)  # Field name made lowercase.
    mainreasondetails = models.TextField(db_column='MainReasonDetails', blank=True, null=True)  # Field name made lowercase.
    schedulereasons = models.TextField(db_column='ScheduleReasons', blank=True, null=True)  # Field name made lowercase.
    schedulemain = models.TextField(db_column='ScheduleMain', blank=True, null=True)  # Field name made lowercase.
    environmentreasons = models.TextField(db_column='EnvironmentReasons', blank=True, null=True)  # Field name made lowercase.
    environmentmain = models.TextField(db_column='EnvironmentMain', blank=True, null=True)  # Field name made lowercase.
    interestreasons = models.TextField(db_column='InterestReasons', blank=True, null=True)  # Field name made lowercase.
    disagreereasons = models.TextField(db_column='DisagreeReasons', blank=True, null=True)  # Field name made lowercase.
    mentalcondition = models.TextField(db_column='MentalCondition', blank=True, null=True)  # Field name made lowercase.
    migrationtype = models.TextField(db_column='MigrationType', blank=True, null=True)  # Field name made lowercase.
    migrationreason = models.TextField(db_column='MigrationReason', blank=True, null=True)  # Field name made lowercase.
    wrongintention = models.TextField(db_column='WrongIntention', blank=True, null=True)  # Field name made lowercase.
    financialreasons = models.TextField(db_column='FinancialReasons', blank=True, null=True)  # Field name made lowercase.
    visaduration = models.TextField(db_column='VisaDuration', blank=True, null=True)  # Field name made lowercase.
    understanding = models.TextField(db_column='Understanding', blank=True, null=True)  # Field name made lowercase.
    sexialityorientation = models.TextField(db_column='SexialityOrientation', blank=True, null=True)  # Field name made lowercase.
    unknowndata = models.TextField(db_column='UnknownData', blank=True, null=True)  # Field name made lowercase.
    fallenreportdate = models.TextField(db_column='FallenReportDate', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    preventable = models.CharField(db_column='Preventable', max_length=50, blank=True, null=True)  # Field name made lowercase.
    preventhow = models.TextField(db_column='PreventHow', blank=True, null=True)  # Field name made lowercase.
    unpreventwhy = models.TextField(db_column='UnpreventWhy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FallenData'


class Faqdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)  # Field name made lowercase.
    question = models.TextField(db_column='Question', blank=True, null=True)  # Field name made lowercase.
    answer = models.TextField(db_column='Answer', blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField(db_column='Active', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FaqData'


class Fruitdata(models.Model):
    fruitkey = models.AutoField(db_column='FruitKey', primary_key=True)  # Field name made lowercase.
    timestamp = models.CharField(db_column='Timestamp', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fishname = models.CharField(db_column='FishName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f1_id = models.CharField(db_column='F1_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    f2_id = models.CharField(db_column='F2_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    f1_points = models.FloatField(db_column='F1_Points', blank=True, null=True)  # Field name made lowercase.
    f2_points = models.FloatField(db_column='F2_Points', blank=True, null=True)  # Field name made lowercase.
    f_time = models.DateTimeField(db_column='F_TIME', blank=True, null=True)  # Field name made lowercase.
    attendee_1_id = models.CharField(db_column='Attendee_1_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attendee_2_id = models.CharField(db_column='Attendee_2_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    a1_points = models.FloatField(db_column='A1_Points', blank=True, null=True)  # Field name made lowercase.
    a2_points = models.FloatField(db_column='A2_Points', blank=True, null=True)  # Field name made lowercase.
    m_time = models.DateTimeField(db_column='M_TIME', blank=True, null=True)  # Field name made lowercase.
    pp1_id = models.CharField(db_column='PP1_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pp2_id = models.CharField(db_column='PP2_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pp1_points = models.FloatField(db_column='PP1_Points', blank=True, null=True)  # Field name made lowercase.
    pp2_points = models.FloatField(db_column='PP2_Points', blank=True, null=True)  # Field name made lowercase.
    pp_time = models.DateTimeField(db_column='PP_TIME', blank=True, null=True)  # Field name made lowercase.
    l1_id = models.CharField(db_column='L1_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    l2_id = models.CharField(db_column='L2_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    l1_points = models.FloatField(db_column='L1_Points', blank=True, null=True)  # Field name made lowercase.
    l2_points = models.FloatField(db_column='L2_Points', blank=True, null=True)  # Field name made lowercase.
    p_time = models.DateTimeField(db_column='P_TIME', blank=True, null=True)  # Field name made lowercase.
    fishuser = models.TextField(db_column='FishUser', blank=True, null=True)  # Field name made lowercase.
    fishphone = models.BigIntegerField(db_column='FishPhone', blank=True, null=True)  # Field name made lowercase.
    # church = models.TextField(db_column='Church', blank=True, null=True)  # Field name made lowercase.
    # fishing_zone = models.TextField(db_column='Fishing_Zone', blank=True, null=True)  # Field name made lowercase.
    # visa = models.TextField(db_column='Visa', blank=True, null=True)  # Field name made lowercase.
    # ev_concept = models.TextField(db_column='EV_Concept', blank=True, null=True)  # Field name made lowercase.
    # evplatform = models.TextField(db_column='EVPlatform', blank=True, null=True)  # Field name made lowercase.
    # evonlineoffline = models.TextField(db_column='EVOnlineOffline', blank=True, null=True)  # Field name made lowercase.
    # birthday = models.CharField(db_column='Birthday', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # state = models.TextField(db_column='State', blank=True, null=True)  # Field name made lowercase.
    # city = models.TextField(db_column='City', blank=True, null=True)  # Field name made lowercase.
    # environment = models.TextField(db_column='Environment', blank=True, null=True)  # Field name made lowercase.
    # notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
    # stage_f = models.CharField(db_column='Stage_F', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # stage_m = models.CharField(db_column='Stage_M', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # stage_p = models.CharField(db_column='Stage_P', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bbt_id = models.CharField(db_column='BBT_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # pls = models.CharField(db_column='PLS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # clad = models.CharField(db_column='CLAD', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # stage_pp = models.CharField(db_column='Stage_PP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # stage = models.CharField(db_column='Stage', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fruitstatus = models.CharField(db_column='FruitStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpdate', blank=True, null=True)  # Field name made lowercase.
    # holidayplan = models.TextField(db_column='HolidayPlan', blank=True, null=True)  # Field name made lowercase.
    # denomination = models.TextField(db_column='Denomination', blank=True, null=True)  # Field name made lowercase.
    # nationality = models.TextField(db_column='Nationality', blank=True, null=True)  # Field name made lowercase.
    # residence = models.TextField(db_column='Residence', blank=True, null=True)  # Field name made lowercase.
    # visanotes = models.TextField(db_column='VisaNotes', blank=True, null=True)  # Field name made lowercase.
    # holidaynotes = models.TextField(db_column='HolidayNotes', blank=True, null=True)  # Field name made lowercase.
    locked = models.CharField(db_column='Locked', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # proceedable = models.CharField(db_column='Proceedable', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # gender = models.CharField(db_column='Gender', max_length=50, blank=True, null=True)  # Field name made lowercase.
    unlockdate = models.DateTimeField(db_column='UnlockDate', blank=True, null=True)  # Field name made lowercase.
    unlockable = models.CharField(db_column='Unlockable', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mine = models.CharField(db_column='Mine', max_length=50, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # social_ig = models.CharField(db_column='Social_IG', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # social_fb = models.CharField(db_column='Social_FB', max_length=50, blank=True, null=True)  # Field name made lowercase.
    uid = AutoUIDField(db_column='UID', unique=True)  # Field name made lowercase.
    exppick = models.DateTimeField(db_column='ExpPick', blank=True, null=True)  # Field name made lowercase.
    expmeet = models.DateTimeField(db_column='ExpMeet', blank=True, null=True)  # Field name made lowercase.

    def save(self, *args, **kwargs):
        if not self.uid:
            # Get the current maximum UID value from the database
            max_uid = Fruitdata.objects.all().aggregate(models.Max('uid'))['uid__max']
            if max_uid:
                self.uid = AutoUIDField().increment_id(max_uid)
            else:
                # If there are no existing records, start with 'A0000'
                self.uid = 'A0000'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.uid
    
    # def __str__(self):
    #     return self.fishname if self.fishname else ''

    class Meta:
        managed = False
        db_table = 'FruitData'


class Gevarecdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tableid = models.IntegerField(db_column='TableID', blank=True, null=True)  # Field name made lowercase.
    record = models.TextField(db_column='Record', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    editdate = models.DateField(db_column='EditDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GevaRecData'


class Gevatabledata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    specs = models.TextField(db_column='Specs', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    editdate = models.DateField(db_column='EditDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GevaTableData'


class Groupdata(models.Model):
    gid = models.AutoField(db_column='GID', primary_key=True)  # Field name made lowercase.
    membergroup = models.CharField(db_column='MemberGroup', max_length=255)  # Field name made lowercase.
    inid = models.IntegerField(db_column='InID', blank=True, null=True)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GroupData'


class Groupfmpgoals(models.Model):
    grp = models.CharField(db_column='Grp', max_length=255, blank=True, null=True)  # Field name made lowercase.
    f = models.FloatField(db_column='F', blank=True, null=True)  # Field name made lowercase.
    m = models.FloatField(db_column='M', blank=True, null=True)  # Field name made lowercase.
    p = models.FloatField(db_column='P', blank=True, null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpdate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GroupFMPGoals'


class Groupinfo(models.Model):
    gid = models.SmallIntegerField(db_column='GID', blank=True, null=True)  # Field name made lowercase.
    grp = models.CharField(db_column='Grp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dept = models.CharField(db_column='Dept', max_length=50, blank=True, null=True)  # Field name made lowercase.
    subdivision = models.CharField(db_column='Subdivision', max_length=50, blank=True, null=True)  # Field name made lowercase.
    division = models.CharField(db_column='Division', max_length=50, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GroupInfo'


class Grouplog(models.Model):
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gid = models.SmallIntegerField(db_column='GID', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GroupLog'


class Innerdeptdata(models.Model):
    inid = models.AutoField(db_column='InID', primary_key=True)  # Field name made lowercase.
    innerdepartment = models.CharField(db_column='InnerDepartment', max_length=255)  # Field name made lowercase.
    did = models.IntegerField(db_column='DID', blank=True, null=True)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'InnerDeptData'


class Innerregiondata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    regionid = models.IntegerField(db_column='RegionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'InnerRegionData'


class Issuereport(models.Model):
    rid = models.AutoField(db_column='RID', primary_key=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rep_description = models.TextField(db_column='Rep_Description', blank=True, null=True)  # Field name made lowercase.
    imagesrc = models.TextField(db_column='ImageSrc', blank=True, null=True)  # Field name made lowercase.
    resolved = models.BooleanField(db_column='Resolved', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'IssueReport'


class Jiraticket(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    jiraid = models.IntegerField(db_column='JiraID', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField(db_column='Timestamp', blank=True, null=True)  # Field name made lowercase.
    senderid = models.CharField(db_column='SenderID', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'JiraTicket'


class Logindata(models.Model):
    id = models.IntegerField(db_column='ID', unique=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=50, unique=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True)  # Field name made lowercase.
    telid = models.BigIntegerField(db_column='TelID', blank=True, null=True)  # Field name made lowercase.
    is_authenticated = models.BooleanField(db_column='Is_Authenticated', blank=True, null=True)  # Field name made lowercase.
    is_anonymous = models.BooleanField(db_column='Is_Anonymous', blank=True, null=True)  # Field name made lowercase.
    is_superuser = models.BooleanField(db_column='Is_Superuser', blank=True, null=True)  # Field name made lowercase.
    is_staff = models.BooleanField(db_column='Is_Staff', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    
    def __str__(self):
        return self.name
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'LoginData'


class Meetingdata(models.Model):
    meetingkey = models.AutoField(db_column='MeetingKey', primary_key=True)  # Field name made lowercase.
    fruitkey = models.CharField(db_column='FruitKey', max_length=50, blank=True, null=True)  # Field name made lowercase.
    meetingnotes = models.TextField(db_column='MeetingNotes', blank=True, null=True)  # Field name made lowercase.
    attendee_1 = models.CharField(db_column='Attendee_1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attendee_2 = models.CharField(db_column='Attendee_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    modifiedby = models.CharField(db_column='ModifiedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    modifieddate = models.TextField(db_column='ModifiedDate', blank=True, null=True)  # Field name made lowercase.
    createddate = models.TextField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    meetingdate = models.TextField(db_column='MeetingDate', blank=True, null=True)  # Field name made lowercase.
    nextmeetingdate = models.TextField(db_column='NextMeetingDate', blank=True, null=True)  # Field name made lowercase.
    metpicker = models.TextField(db_column='MetPicker', blank=True, null=True)  # Field name made lowercase.
    proceedable = models.TextField(db_column='Proceedable', blank=True, null=True)  # Field name made lowercase.
    reasonunproceedable = models.TextField(db_column='ReasonUnproceedable', blank=True, null=True)  # Field name made lowercase.
    bbt_id = models.CharField(db_column='BBT_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    outcome = models.CharField(db_column='Outcome', max_length=255, blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MeetingData'


class Memberdata(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name', blank=True, null=True)  # Field name made lowercase.
    membergroup = models.CharField(db_column='MemberGroup', max_length=50, blank=True, null=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=50, blank=True, null=True)  # Field name made lowercase.
    group_imwy = models.CharField(db_column='Group_IMWY', max_length=50, blank=True, null=True)  # Field name made lowercase.
    internal_position = models.TextField(db_column='Internal_Position', blank=True, null=True)  # Field name made lowercase.
    # internal_title = models.TextField(db_column='Internal_Title', blank=True, null=True)  # Field name made lowercase.
    # tgw = models.BooleanField(db_column='TGW', blank=True, null=True)  # Field name made lowercase.
    registered = models.BooleanField(db_column='Registered', blank=True, null=True)  # Field name made lowercase.
    bbt = models.BooleanField(db_column='BBT', blank=True, null=True)  # Field name made lowercase.
    # btm = models.TextField(db_column='BTM', blank=True, null=True)  # Field name made lowercase.
    # first_name = models.TextField(db_column='FIRST_NAME', blank=True, null=True)  # Field name made lowercase.
    # middle_name = models.TextField(db_column='MIDDLE_NAME', blank=True, null=True)  # Field name made lowercase.
    # last_name = models.TextField(db_column='LAST_NAME', blank=True, null=True)  # Field name made lowercase.
    # preferred_name = models.TextField(db_column='PREFERRED_NAME', blank=True, null=True)  # Field name made lowercase.
    # k_name = models.TextField(db_column='K_NAME', blank=True, null=True)  # Field name made lowercase.
    username = models.TextField(db_column='UserName', unique=True, null=True)  # Field name made lowercase.
    password = models.TextField(db_column='PassWord', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=255, blank=True, unique=True)  # Field name made lowercase.
    
    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'MemberData'



class Membergrouplog(models.Model):
    cycle = models.IntegerField(db_column='Cycle')  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=255, blank=True, null=True)  # Field name made lowercase.
    membergroup = models.CharField(db_column='MemberGroup', max_length=50, blank=True, null=True)  # Field name made lowercase.
    group_imwy = models.CharField(db_column='Group_IMWY', max_length=50, blank=True, null=True)  # Field name made lowercase.
    internal_position = models.TextField(db_column='Internal_Position', blank=True, null=True)  # Field name made lowercase.
    logdate = models.DateTimeField(db_column='LogDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MemberGroupLog'


class Memberlogindata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mid = models.IntegerField(db_column='MID')  # Field name made lowercase.
    logintime = models.DateTimeField(db_column='LoginTime', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MemberLoginData'


class Memberuserdata(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255)  # Field name made lowercase.
    last_login = models.DateTimeField(db_column='Last_Login', blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=255, blank=True, null=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='First_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    is_staff = models.BooleanField(db_column='Is_Staff', blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='Is_Active', blank=True, null=True)  # Field name made lowercase.
    is_authenticated = models.BooleanField(db_column='Is_Authenticated', blank=True, null=True)  # Field name made lowercase.
    date_joined = models.DateTimeField(db_column='Date_Joined', blank=True, null=True)  # Field name made lowercase.
    is_anonymous = models.BooleanField(db_column='Is_Anonymous', blank=True, null=True)  # Field name made lowercase.
    is_superuser = models.BooleanField(db_column='Is_Superuser', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MemberUserData'


class Missedudata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=50, blank=True, null=True)  # Field name made lowercase.
    expecteddate = models.DateTimeField(db_column='ExpectedDate', blank=True, null=True)  # Field name made lowercase.
    reportdate = models.DateField(db_column='ReportDate', blank=True, null=True)  # Field name made lowercase.
    revived = models.CharField(db_column='Revived', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MissEduData'


class Ncttransferdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    moredetail = models.TextField(db_column='MoreDetail', blank=True, null=True)  # Field name made lowercase.
    oldct = models.IntegerField(db_column='OldCT', blank=True, null=True)  # Field name made lowercase.
    newct = models.IntegerField(db_column='NewCT', blank=True, null=True)  # Field name made lowercase.
    allowed = models.IntegerField(db_column='Allowed', blank=True, null=True)  # Field name made lowercase.
    reportdate = models.DateTimeField(db_column='ReportDate', blank=True, null=True)  # Field name made lowercase.
    bbt = models.CharField(db_column='BBT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    approver = models.CharField(db_column='Approver', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'NCTTransferData'


class OldPosition(models.Model):
    memberkey = models.AutoField(db_column='MemberKey', primary_key=True)  # Field name made lowercase.
    memberid = models.IntegerField(db_column='MemberId', blank=True, null=True)  # Field name made lowercase.
    grp = models.CharField(db_column='Grp', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sft_grp = models.CharField(db_column='SFT_Grp', max_length=10, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=20, blank=True, null=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    istgw = models.BooleanField(db_column='IsTGW', blank=True, null=True)  # Field name made lowercase.
    istgw_sft = models.BooleanField(db_column='IsTGW_SFT', blank=True, null=True)  # Field name made lowercase.
    isedu = models.BooleanField(db_column='IsEdu', blank=True, null=True)  # Field name made lowercase.
    isev = models.BooleanField(db_column='IsEV', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'OLD_Position'

class Otplog(models.Model):
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    otp = models.IntegerField(db_column='OTP', blank=True, null=True)  # Field name made lowercase.
    validuntil = models.DateTimeField(db_column='ValidUntil', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'OtpLog'


class Ppresponsedata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bbt = models.CharField(db_column='BBT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    meetingkey = models.IntegerField(db_column='MeetingKey', blank=True, null=True)  # Field name made lowercase.
    response = models.CharField(db_column='Response', max_length=50, blank=True, null=True)  # Field name made lowercase.
    logdate = models.DateTimeField(db_column='LogDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PPResponseData'


class Pickinglogdata(models.Model):
    pid = models.AutoField(db_column='PID', primary_key=True)  # Field name made lowercase.
    bbt = models.CharField(db_column='BBT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fruitkey = models.IntegerField(db_column='FruitKey', blank=True, null=True)  # Field name made lowercase.
    logdate = models.DateTimeField(db_column='LogDate', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PickingLogData'


class Position(models.Model):
    pid = models.SmallIntegerField(db_column='PID', blank=True, null=True)  # Field name made lowercase.
    division = models.CharField(db_column='Division', max_length=50, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Position'


class Ref(models.Model):
    category = models.CharField(db_column='Category', max_length=50, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ref'


class Regiondata(models.Model):
    rid = models.AutoField(db_column='RID', primary_key=True)  # Field name made lowercase.
    region = models.CharField(db_column='Region', max_length=255)  # Field name made lowercase.
    position = models.IntegerField(db_column='Position', blank=True, null=True)  # Field name made lowercase.
    abbr = models.CharField(db_column='Abbr', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'RegionData'


class Registration(models.Model):
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    evid = models.SmallIntegerField(db_column='EVID', blank=True, null=True)  # Field name made lowercase.
    keysname = models.CharField(db_column='KeysName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    offid = models.SmallIntegerField(db_column='OffID', blank=True, null=True)  # Field name made lowercase.
    prefname = models.CharField(db_column='PrefName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    givname = models.CharField(db_column='GivName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    othergiv = models.CharField(db_column='OtherGiv', max_length=50, blank=True, null=True)  # Field name made lowercase.
    surname = models.CharField(db_column='Surname', max_length=50, blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    unit = models.SmallIntegerField(db_column='Unit', blank=True, null=True)  # Field name made lowercase.
    streetno = models.SmallIntegerField(db_column='StreetNo', blank=True, null=True)  # Field name made lowercase.
    streetname = models.CharField(db_column='StreetName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    suburb = models.CharField(db_column='Suburb', max_length=50, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=50, blank=True, null=True)  # Field name made lowercase.
    postcode = models.SmallIntegerField(db_column='PostCode', blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=50, blank=True, null=True)  # Field name made lowercase.
    countrycode = models.SmallIntegerField(db_column='CountryCode', blank=True, null=True)  # Field name made lowercase.
    phone = models.IntegerField(db_column='Phone', blank=True, null=True)  # Field name made lowercase.
    ct = models.CharField(db_column='CT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    scjid = models.CharField(db_column='SCJID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    imwy = models.CharField(db_column='IMWY', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Registration'


class Report(models.Model):
    reportid = models.AutoField(db_column='ReportId', primary_key=True)  # Field name made lowercase.
    # bbid = models.ForeignKey('Bbdata', on_delete=models.DO_NOTHING, db_column='BBID')  # Field name made lowercase.
    reportdate = models.CharField(db_column='ReportDate', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    classdate = models.CharField(db_column='ClassDate', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    createdby = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='CreatedBy', max_length=50, blank=True, null=True, to_field='uid', related_name='report_cr_uid')  # Field name made lowercase.
    topic = models.CharField(db_column='Topic', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    beforeclass = models.CharField(db_column='BeforeClass', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    duringclass = models.CharField(db_column='DuringClass', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    afterclass = models.CharField(db_column='AfterClass', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    general = models.CharField(db_column='General', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    obedience = models.CharField(db_column='Obedience', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    friendcircumstances = models.CharField(db_column='FriendCircumstances', max_length=1200, blank=True, null=True)  # Field name made lowercase.
    nextclassdate = models.DateTimeField(db_column='NextClassDate', blank=True, null=True)  # Field name made lowercase.
    attendee_1 = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='Attendee_1', max_length=50, blank=True, null=True, to_field='uid', related_name='report_a1_uid')  # Field name made lowercase.
    attendee_2 = models.ForeignKey('Memberdata', on_delete=models.DO_NOTHING, db_column='Attendee_2', max_length=50, blank=True, null=True, to_field='uid', related_name='report_a2_uid')  # Field name made lowercase.
    additionalinfo = models.TextField(db_column='AdditionalInfo', blank=True, null=True)  # Field name made lowercase.
    reaction = models.TextField(db_column='Reaction', blank=True, null=True)  # Field name made lowercase.
    attitude = models.TextField(db_column='Attitude', blank=True, null=True)  # Field name made lowercase.
    environment = models.TextField(db_column='Environment', blank=True, null=True)  # Field name made lowercase.
    bbt_feedback = models.TextField(db_column='BBT_Feedback', blank=True, null=True)  # Field name made lowercase.
    label = models.TextField(db_column='Label', blank=True, null=True)  # Field name made lowercase.
    ispicking = models.BooleanField(db_column='IsPicking', blank=True, null=True)  # Field name made lowercase.
    uid = models.ForeignKey('Bbdata', on_delete=models.DO_NOTHING, db_column='UID', max_length=50, to_field='uid', related_name='rep')  # Field name made lowercase.
    # stud = models.ForeignKey(Bbdata, on_delete=models.CASCADE, blank=True, null=True, related_name='reports')  # Field name made lowercase.
    # uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # fruitkey = models.CharField(db_column='FruitKey', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # topicid = models.IntegerField(db_column='TopicID', blank=True, null=True)  # Field name made lowercase.
    # bbtype = models.CharField(db_column='BBType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # bblocation = models.CharField(db_column='BBLocation', max_length=255, blank=True, null=True)  # Field name made lowercase.
    # ontime = models.CharField(db_column='OnTime', max_length=255, blank=True, null=True)  # Field name made lowercase.
    # feedbackbbt = models.CharField(db_column='FeedbackBBT', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # ctschedule = models.CharField(db_column='CTSchedule', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # duration = models.CharField(db_column='Duration', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # classcontent = models.CharField(db_column='ClassContent', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # specialmindset = models.TextField(db_column='SpecialMindset', blank=True, null=True)  # Field name made lowercase.
    # skillandreaction = models.TextField(db_column='SkillAndReaction', blank=True, null=True)  # Field name made lowercase.
    # revision = models.CharField(db_column='Revision', max_length=50, blank=True, null=True)  # Field name made lowercase.
    # skillandreaction2 = models.TextField(db_column='SkillAndReaction2', blank=True, null=True)  # Field name made lowercase.
    # mainconcern = models.CharField(db_column='MainConcern', max_length=255, blank=True, null=True)  # Field name made lowercase.
    # mainconcerndetails = models.TextField(db_column='MainConcernDetails', blank=True, null=True)  # Field name made lowercase.
    # concerns = models.TextField(db_column='Concerns', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Report'

class ProImage(models.Model):
    product = models.ForeignKey(Memberdata, on_delete=models.CASCADE, related_name="pro_uid")
    image = models.ImageField(upload_to="img", default="", null=True, blank=True)


class Reportmotivationdata(models.Model):
    rid = models.AutoField(db_column='RID', primary_key=True)  # Field name made lowercase.
    quote = models.TextField(db_column='Quote', blank=True, null=True)  # Field name made lowercase.
    category = models.TextField(db_column='Category', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ReportMotivationData'


class Sftmemberdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    team = models.CharField(db_column='TEAM', max_length=50, blank=True, null=True)  # Field name made lowercase.
    leader = models.IntegerField(db_column='Leader', blank=True, null=True)  # Field name made lowercase.
    sftid = models.IntegerField(db_column='SFTID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SFTMemberData'


class Scotttesttable(models.Model):
    testcolumn = models.IntegerField(db_column='TestColumn', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ScottTestTable'


class Serviceabsentdata(models.Model):
    aid = models.AutoField(db_column='AID', primary_key=True)  # Field name made lowercase.
    memberid = models.CharField(db_column='MemberID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    absentcounter = models.IntegerField(db_column='AbsentCounter', blank=True, null=True)  # Field name made lowercase.
    absentcumulative = models.IntegerField(db_column='AbsentCumulative', blank=True, null=True)  # Field name made lowercase.
    lastreport = models.CharField(db_column='LastReport', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ServiceAbsentData'


class Servicedata(models.Model):
    sid = models.AutoField(db_column='SID', primary_key=True)  # Field name made lowercase.
    servicedate = models.DateField(db_column='ServiceDate', blank=True, null=True)  # Field name made lowercase.
    serviceday = models.CharField(db_column='ServiceDay', max_length=50, blank=True, null=True)  # Field name made lowercase.
    servicetitle = models.TextField(db_column='ServiceTitle', blank=True, null=True)  # Field name made lowercase.
    maintime = models.CharField(db_column='MainTime', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ServiceData'


class Suburbdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    innerregionid = models.IntegerField(db_column='InnerRegionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SuburbData'


class Tgwpositionlog(models.Model):
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    tid = models.SmallIntegerField(db_column='TID', blank=True, null=True)  # Field name made lowercase.
    pid = models.SmallIntegerField(db_column='PID', blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TGWPositionLog'


class Task(models.Model):
    tid = models.SmallIntegerField(db_column='TID', blank=True, null=True)  # Field name made lowercase.
    task = models.CharField(db_column='Task', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Task'


class Telegrambotdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    active = models.IntegerField(db_column='Active', blank=True, null=True)  # Field name made lowercase.
    access = models.CharField(db_column='Access', max_length=10, blank=True, null=True)  # Field name made lowercase.
    accesscode = models.IntegerField(db_column='AccessCode', blank=True, null=True)  # Field name made lowercase.
    telid = models.BigIntegerField(db_column='TelID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'TelegramBotData'


class Todo(models.Model):
    taskid = models.AutoField(db_column='TaskID', primary_key=True)  # Field name made lowercase.
    memberid = models.IntegerField(db_column='MemberId', blank=True, null=True)  # Field name made lowercase.
    createddate = models.DateTimeField(db_column='CreatedDate', blank=True, null=True)  # Field name made lowercase.
    completedate = models.DateTimeField(db_column='CompleteDate', blank=True, null=True)  # Field name made lowercase.
    tasktitle = models.CharField(db_column='TaskTitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    taskdescription = models.CharField(db_column='TaskDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(db_column='Category', max_length=255, blank=True, null=True)  # Field name made lowercase.
    iscompleted = models.TextField(db_column='IsCompleted', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    participants = models.CharField(db_column='Participants', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Todo'


class Unsuccessfulpickingdata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    bbt_id = models.CharField(db_column='BBT_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    student = models.CharField(db_column='Student', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(db_column='Reason', blank=True, null=True)  # Field name made lowercase.
    reportedby = models.CharField(db_column='ReportedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reporteddate = models.DateField(db_column='ReportedDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'UnsuccessfulPickingData'


class Watchlistdata(models.Model):
    watchid = models.AutoField(db_column='WatchID', primary_key=True)  # Field name made lowercase.
    memberid = models.CharField(db_column='MemberID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    addeddate = models.DateField(db_column='AddedDate', blank=True, null=True)  # Field name made lowercase.
    addedby = models.CharField(db_column='AddedBy', max_length=50, blank=True, null=True)  # Field name made lowercase.
    unwatched = models.BooleanField(db_column='Unwatched', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WatchListData'


class Weekgoaldata(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    goal = models.TextField(db_column='GOAL', blank=True, null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    goaldate = models.DateField(db_column='GoalDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WeekGoalData'


class Whitelistdata(models.Model):
    wid = models.AutoField(db_column='WID', primary_key=True)  # Field name made lowercase.
    title = models.TextField(db_column='Title')  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    data = models.TextField(db_column='Data', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WhiteListData'


class Whitelistrecdata(models.Model):
    wid = models.AutoField(db_column='WID', primary_key=True)  # Field name made lowercase.
    memberid = models.CharField(db_column='MemberID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    wlid = models.IntegerField(db_column='WLID')  # Field name made lowercase.
    addeddate = models.TextField(db_column='AddedDate', blank=True, null=True)  # Field name made lowercase.
    addedby = models.IntegerField(db_column='AddedBy', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WhiteListRecData'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class MemberMultiFactorToken(models.Model):
    uid = models.CharField(primary_key=True, max_length=6)
    token = models.CharField(max_length=6)
    active = models.BooleanField(blank=True, null=True)
    created_utc = models.DateTimeField(db_column='created_UTC', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'member_multi_factor_token'
        unique_together = (('uid', 'token'),)
