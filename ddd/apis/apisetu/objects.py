# Define onjects for all entities in client APISETU

class StateObject:
    state_id: int
    state_name: str

class DistrictObject:
    district_id: int
    district_name: str
    
class Center:
    center_id: int
    name: str
    name_l: str
    address: str
    state_name: str
    district_name: str
    block_name: str
    pincode: int
    _from: str
    to: str
    
class SessionObject:
    session_id: int
    date: str
    available_capacity: str
    min_age_limit: int
    vaccine: str
    slots: list
    