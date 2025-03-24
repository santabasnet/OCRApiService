# Represents all the available forms
import json
from dataclasses import dataclass
from typing import List
from dacite import from_dict
import numpy as Num
import os

from com.iict.ocr import FileUtils
from com.iict.ocr.FieldInfo import FieldInfo


@dataclass(init=True)
class Semantics:
    ocrType: str
    availableCharacters: str
    boundingBox: str


@dataclass(init=True)
class Corner:
    x: int
    y: int

    def point(self):
        return self.x, self.y


@dataclass(init=True)
class Location:
    label: str
    topLeft: Corner
    bottomRight: Corner

    def fieldInfo(self):
        return FieldInfo(
            x=self.topLeft.x,
            y=self.topLeft.y,
            width=self.bottomRight.x - self.topLeft.x,
            height=self.bottomRight.y - self.topLeft.y
        )


@dataclass(init=True)
class FormField:
    pageNo: int
    name: str
    semantics: Semantics
    locations: List[Location]

    # Returns the list of field locations. It contains all the field information
    # for the OCR.
    def allLocations(self):
        return self.locations

    # Returns the list of field information of their coordinates.
    def locationFields(self):
        return [location.fieldInfo() for location in self.locations]

    # Return the name of the field.
    def getName(self):
        return self.name


@dataclass(init=True)
class BankForm:
    institution: str
    formTitle: str
    formType: str
    formFields: List[FormField]

    def listOfLocations(self):
        return [f.getLocations() for f in self.formFields]

    def fieldPages(self):
        return Num.unique([field.pageNo for field in self.formFields])

    def pageLocations(self, pageNo):
        return [field.locations for field in self.formFields if field.pageNo == pageNo]

    def pageFields(self, pageNo):
        return [field for field in self.formFields if field.pageNo == pageNo]


@dataclass(init=True)
class AllForm:
    allForms: List[BankForm]

    def count(self) -> int:
        return len(self.allForms)


# Json configuration file for OCR definition.
fileName = 'assets/config/field_info.json'


# Read JSON configuration.
def jsonContentOf(givenFileName):
    # Open a file: file
    file = open(givenFileName, mode='r')
    # read all lines at once
    jsonContent = file.read()
    # close the file
    file.close()
    return jsonContent


# Load the JSON content with
ocrDefinitionDict = json.loads(jsonContentOf(fileName))

# Load the definition in Json Data class.
ocrDefinition: AllForm = from_dict(AllForm, ocrDefinitionDict)


# Extract all the pages from the JSON definition.
def allPages():
    return ocrDefinition.allForms[0].fieldPages()


# Extract all the locations from the given page number.
def allPageLocation(pageNo):
    return ocrDefinition.allForms[0].pageLocations(pageNo)


# Extract all form fields for the given page no.
def allPageFields(pageNo):
    return ocrDefinition.allForms[0].pageFields(pageNo)


# Source Template file names definition.
allSourcePages = {
    1: "Im1_1.jpeg",
    2: "Im2_2.jpeg",
    3: "Im3_3.jpeg",
    4: "Im4_4.jpeg",
    5: "Im5_5.jpeg",
    6: "Im6_6.jpeg",
    7: "Im7_7.jpeg",
    8: "Im8_8.jpeg",
    9: "Im9_9.jpeg",
    10: "Im10_10.jpeg",
    11: "Im11_11.jpeg",
    12: "Im12_12.jpeg",
    13: "Im13_13.jpeg",
}


# Get file name for the page index.
def templateFileNameOf(pageNo):
    filePath = os.path.join(FileUtils.TEMPLATES_FOLDER, allSourcePages.get(pageNo) or '')
    return filePath


# Get all the template file names
def allTemplateFileNames():
    return [templateFileNameOf(index) for (index, _) in allSourcePages.items()]


# Read all the template files in the image format.
def allTemplateImages():
    return [FileUtils.readImage(templateName) for templateName in allTemplateFileNames()]


# Extract field definition of the given page number and return list of form field.
def fieldDefinitionOf(pageNo, institution="Nabil Bank") -> list[FormField]:
    institutionDefinition = [form for form in ocrDefinition.allForms if form.institution == institution][0] or None
    if institutionDefinition is None:
        return []
    else:
        return [field for field in institutionDefinition.formFields if field.pageNo == pageNo]


# Field Definition extraction.
def fieldDefinitionWithName(fieldName, pageNo, institution="Nabil Bank") -> FormField:
    fields = [pageField for pageField in fieldDefinitionOf(pageNo, institution) if pageField.name == fieldName]
    return fields[0] if fields else None


# Extract the field definition tick mark of the given page and institution with field name.
def fieldTickMark(fieldName, pageNo, institution="Nabil Bank") -> FormField:
    return fieldDefinitionWithName(fieldName, pageNo, institution)


# Extract the semantic information of the field.
def extractSemanticInfo(fieldName, pageNo, institution="Nabil Bank"):
    fieldDefinition = fieldDefinitionWithName(fieldName, pageNo, institution)
    return fieldDefinition.semantics if fieldDefinition else None


# Read Image File
# = [FileUtils.readImage(templateFileNameOf(index)) for (index, _) in allSourcePages.items()]
# [print(image.shape) for image in images]
