import uuid

def hex_uuid():
    return uuid.uuid1().hex[::-1]

