import re

def verify_kyc(pan, aadhaar):
    pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    aadhaar_pattern = r"^\d{12}$"

    if re.match(pan_pattern, pan) and re.match(aadhaar_pattern, aadhaar):
        return True
    return False