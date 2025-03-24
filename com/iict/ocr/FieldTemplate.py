# Field Template definition.
from com.iict.ocr.FieldInfo import FieldInfo


class FieldTemplate:
    def __init__(self, fieldName='', fieldInfo=FieldInfo()):
        self.fieldName = fieldName
        self.fieldInfo = fieldInfo

    def isEmpty(self):
        return (not self.fieldName) or self.fieldInfo.isEmpty()

    def getFieldInfo(self):
        return self.fieldInfo

    def getName(self):
        return self.fieldName

