# Documents Field definition.
from com.iict.jsondata import BankForms
from com.iict.jsondata.BankForms import FormField
from com.iict.ocr.FieldInfo import FieldInfo
from com.iict.ocr.FieldTemplate import FieldTemplate

# Account type.
ACCOUNT_TYPE = 'Please open an account in your Bank with following details.'
CURRENCY = 'Currency'

# Account Holder Full Name.
ACCOUNT_FULL_NAME = 'Account Full Name'

# Minor/Legal Guardian Information
NAME_OF_GUARDIAN = 'Name of Guardian'
RELATIONSHIP = 'Relationship'

# Personal Information.
PERSONAL_FULL_NAME = 'Personal Full Name'
DATE_OF_BIRTH = 'Date of Birth (B.S.)'
DATE_OF_BIRTH_AD = 'Date of Birth (A.D.)'
NATIONALITY = 'Nationality'
GENDER = 'Gender'
MARITAL_STATUS = 'Marital Status'
LANDLINE_PHONE = 'Landline'
MOBILE_PHONE = 'Mobile'
EMAIL_ADDRESS = 'Email'

# Permanent Address.
PERMANENT_DISTRICT = 'District'
PERMANENT_MUNICIPALITY = 'Metro P/Sub Metro P./Muni./R. Municipality'
PERMANENT_WARD_NO = 'Ward No'
PERMANENT_TOLE_STREET = 'Tole/Street'
PERMANENT_HOUSE_NO = 'House No'
PERMANENT_PROVINCE = 'Province'
PERMANENT_COUNTRY = 'Country'

# Current Address.
CURRENT_DISTRICT = 'District'
CURRENT_MUNICIPALITY = 'Metro P/Sub Metro P./Muni./R. Municipality'
CURRENT_WARD_NO = 'Ward No'
CURRENT_TOLE_STREET = 'Tole/Street'
CURRENT_HOUSE_NO = 'House No'
CURRENT_PROVINCE = 'Province'
CURRENT_COUNTRY = 'Country'
CURRENT_HOUSE_OWNER = 'In case of Tenant, Name of House Owner'
CURRENT_CONTACT_NO = 'Contact No.'

# Identification Details.
CITIZENSHIP = 'Citizenship'
DRIVING_LICENSE = 'Driving License'
VOTER_ID = 'Voter ID'
PASSPORT = 'Passport'
EMBASSY_REGD_CARD = 'Embassy Regd. Card'
BIRTH_CERTIFICATE = 'BIRTH CERTIFICATE'
MINOR_ID = 'Minor ID'
ID_NUMBER = 'ID Number'
ISSUE_DATE = 'Issue Date'
EXPIRY_DATE = 'Expiry Date'
ISSUING_AUTHORITY = 'Issuing Authority'
PLACE_OF_ISSUE = 'Place of Issue'

# Visa Details (For Foreign Nationals Only)
VISA_ISSUE_DATE = 'Visa Issue Date'
VISA_VALIDITY = 'Visa Validity'
PAN = 'PAN'
PAN_NOT_AVAILABLE = 'PAN not available'

# Global definition.
# Default Image Dimension
IMAGE_HEIGHT = 2059
IMAGE_WIDTH = 1408

# Dimension for Account full name.
accountFullName = FieldTemplate(ACCOUNT_FULL_NAME, FieldInfo(8, 586, 700, 43))

# Dimension for Personal information.
personalFullName = FieldTemplate(PERSONAL_FULL_NAME, FieldInfo(8, 880, 700, 43))

# Dimension for Contact details.

# Dimension for permanent address.
district = FieldTemplate(PERMANENT_DISTRICT, FieldInfo(8, 1346, 398, 35))

placeOfIssue = FieldTemplate(PLACE_OF_ISSUE, FieldInfo(660, 1887, 290, 35))


# returns the field information.
def ocrFields():
    fields = [accountFullName, personalFullName, district, placeOfIssue]
    return fields


# Return OCR field from the template definition of JSON configuration.
def ocrFromTemplateFields(pageNo) -> list[FormField]:
    return BankForms.fieldDefinitionOf(pageNo)
