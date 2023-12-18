# Define all the constants being used by APISETU

HOST_URL = "https://cdn-api.co-vin.in/api/"
STATE_URL = HOST_URL + "/v2/admin/location/states"
DISTRICT_URL = HOST_URL + "/v2/admin/location/districts/{state_id}"
APPOINTMENT_BY_DIST = HOST_URL + "/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}"
APPOINTMENT_BY_PIN = HOST_URL + "/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={date}"