# Field value extraction by utilizing bounding box, ocr and language model.
from typing import List

from com.iict.jsondata.BankForms import fieldTickMark, extractSemanticInfo
from com.iict.ocr.BoundingWindows import TickWindows, BoundingWindows
import numpy as np
from PIL import Image

from com.iict.ocr.OCRApi import Document
from com.iict.ocr.TextDetection import TextDetection

# Initialize the document model for text extraction.
DOCUMENT_MODEL = Document()

# DOCUMENT_MODEL = None
# All name fields.
nameFields = ["applicantName", "landlordName", "minorGuardiansName", "mothersName", "grandFatherName",
              "grandMotherName", "husbandWifeName", "accountPurpose"]


def _isToProcessIndividual(fieldName):
    return fieldName in nameFields


# Convert numpy array image to PIL image.
def pilImageOf(image):
    return Image.fromarray(np.uint8(image)).convert('RGB')


# Has empty image.
def isEmptyImage(image):
    return image.size == (0, 0)


# Perform OCR for an image slice, it is numpy array.
# which means, it is converted PIL image to perform
# OCR operation.
def ocrText(image, fieldName):
    # Process the given image for any unnecessary bounding spaces.
    images = []
    if _isToProcessIndividual(fieldName):
        images.extend(TextDetection(image).detect())
    else:
        images.append(image)

    pilImages = [pilImageOf(img) for img in images]
    ocrImage = lambda newImage: "" if isEmptyImage(newImage) else DOCUMENT_MODEL.extract(newImage)[0]
    ocrResults = [ocrImage(img) for img in pilImages]

    # Convert numpy image to PIL image to perform OCR.
    # newImage = pilImageOf(image)
    # return "" if isEmptyImage(newImage) else DOCUMENT_MODEL.extract(newImage)[0]

    return " ".join(ocrResults)


# Perform OCR for the list of images.
def ocrTextList(fieldImages):
    def subImages(name, fImage):
        fImages = []
        if _isToProcessIndividual(name):
            fImages.extend(TextDetection(fImage).detect())
        else:
            fImages.append(fImage)
        return fImages

    fieldImagesIndices = [(name, subImages(name, image)) for (name, image) in fieldImages]
    fieldImages = []
    for (_, images) in fieldImagesIndices:
        fieldImages.extend([pilImageOf(image) for image in images])

    # print(f'Field Info >> {len(fieldImagesIndices)}: {len(fieldImages)}')
    # Acquire the batch ocr results in the form of text list.
    ocrTextResults = DOCUMENT_MODEL.extract(fieldImages)

    # Re-group the batch field results.
    fieldSubLists = [(name, len(images)) for (name, images) in fieldImagesIndices]
    gIndex = 0
    groupedResult = []
    for (fName, fSize) in fieldSubLists:
        result = " ".join(ocrTextResults[gIndex:gIndex + fSize])
        groupedResult.append((fName, [result]))
        gIndex = gIndex + fSize

    return groupedResult


# Perform OCR for an image slice and return the list of text segments.
def ocrSegments(image):
    newImage = pilImageOf(image)
    return [] if isEmptyImage(newImage) else DOCUMENT_MODEL.extractSegments(newImage)


def isWhiteSpace(ch):
    return ch == ' ' or ch == '\r' or ch == '\n'


def isDateSymbols(ch):
    return ch == '|' or ch == '/' or ch == '_' or ch == '-'


def keepAlphabets(segment):
    return "".join([ch for ch in segment if ch.isalpha() or isWhiteSpace(ch)])


def keepNumbers(segment):
    return "".join([ch for ch in segment if ch.isdigit() or isDateSymbols(ch) or isWhiteSpace(ch)])


class FieldExtraction:

    # Default constructor for initialization required variables.
    def __init__(self, pageNo, fieldName, images):
        self.images = images
        self.fieldName = fieldName
        self.pageNo = pageNo

    # Needs to check whether the field name is of tick mark type or not. [From the config file.]
    # Right now, the simple method, check whether it is of single image or multiple one.
    def __isTickMark(self):
        return len(self.images) > 1

    # Process the label name for the tick mark.
    def __extractTickLabel(self, tickField):
        extractedIndices = [index for index, image in enumerate(self.images) if TickWindows(image).hasTickMark()]
        return [tickField.locations[index].label for index in extractedIndices]

    # Process tick mark, find the field name if available as the tick mark.
    def __processTickMark(self):
        # List out the tick mark with the given field and page number, pageNo starts from 0 and
        # configuration file has starting from 1.
        tickField = fieldTickMark(self.fieldName, self.pageNo + 1)
        return [] if not tickField else self.__extractTickLabel(tickField)

    # Perform text cleaning base on the language model.
    def __cleanText(self, ocrOutput) -> list[list[str]]:
        # 1. Extract all the viterbi paths for the generated string.
        # 2. Find Unique one.
        # 3. Perform cleaning text, whether it is of number of text field.
        # 4. Find Suggestion from SOLR server.

        def cleanCharacters(segments: list[str]) -> list[str]:
            match extractSemanticInfo(self.fieldName, self.pageNo + 1).availableCharacters:
                case 'alphabets':
                    onlyAlphabets = [keepAlphabets(segment) for segment in segments]
                    return [text for text in onlyAlphabets if len(text.strip()) > 0]
                case 'numbers':
                    onlyNumbers = [keepNumbers(segment) for segment in segments]
                    return [text for text in onlyNumbers if len(text.strip()) > 0]
                case _:
                    return [segment for segment in segments if len(segment.strip()) > 0]

        # Perform cleaning.
        cleanTexts = [cleanCharacters(segments) for segments in ocrOutput]

        # Remove duplicates after cleaning.
        uniqueTexts = {"".join(texts): texts for texts in cleanTexts}.values()

        # Remove empty items after cleaning.
        return [segment for segment in uniqueTexts if segment]

    def __cleanStr(self, text):
        match extractSemanticInfo(self.fieldName, self.pageNo + 1).availableCharacters:
            case 'alphabets':
                return keepAlphabets([*text]).strip()
            case 'numbers':
                return keepNumbers([*text]).strip()
            case _:
                return text.strip()

    # Process image ocr.
    def __processOCR(self):

        # Crop the image based on the bounding box analysis.
        # croppedImages = [BoundingWindows(image).croppedImage() for image in self.images]
        textImages = [image for image in self.images if BoundingWindows(image).hasMinimumBoxes()]

        # Build a list of field name and the tuple for batch extraction.
        # fieldOCRList = {}

        ocrList = [ocrText(image, self.fieldName) for image in textImages]
        cleanedText = [self.__cleanStr(text) for text in ocrList]

        ########
        # for image in textImages:
        # cleanedSegments = self.__cleanText(ocrSegments(image))
        # suggested =
        # print(f'{self.fieldName} is cleaned with result >> {cleanedSegments}')
        # print()

        return cleanedText

    def extract(self):
        return self.__processTickMark() if self.__isTickMark() else self.__processOCR()


# Holds for the multiple type of image recognition.
class ImageRecognition:
    def __init__(self, batchList):
        self.batchList = batchList
        self.ocrBatch = []
        self.tickBatch = []
        # separate the batch list for tick mark and the ocr images.
        for (slicedName, slicedImages) in batchList:
            if len(slicedImages) > 1:
                self.tickBatch.append((slicedName, slicedImages))
            else:
                self.ocrBatch.append((slicedName, slicedImages))

    def ocrTypes(self):
        return self.ocrBatch

    def tickTypes(self):
        return self.tickBatch

    def tickAndOcrTypes(self):
        return self.tickBatch, [(name, images[0]) for (name, images) in self.ocrBatch]


# Batch OCR for given lists of fields.
# Batches have list of dictionary that contains,
# imageSlices, an imageSlice is the object of field name and the list of images.
class BatchExtraction:

    # Default constructor.
    def __init__(self, pageNo, batchSlices):
        self.pageNo = pageNo
        self.batchSlices = batchSlices

    # Perform external call here for the OCR result.
    def extract(self):
        batchList = list(self.batchSlices.items())

        # Store the field sequences to accumulate the OCR results.
        fieldNames = [fieldName for (fieldName, _) in batchList]

        # Separate the tick mark images and the ocr type images.
        tickBatchList, ocrBatchList = ImageRecognition(batchList).tickAndOcrTypes()

        # Extract the tick marks.
        tickMarkResults = self.__processTickBatch(tickBatchList)

        # Extract the text from images.
        ocrResult = self.__processOCRBatch(ocrBatchList)

        # Combine all the extraction result.
        results = {name: (ocrResult[name] if name in ocrResult else tickMarkResults[name]) for name in fieldNames}

        return results

    # Process tick mark, find the field name if available as the tick mark.
    def __processTickBatch(self, tickMarks):

        # Process the label name for the tick mark.
        def extractTickLabel(tickField, images):
            extractedIndices = [index for index, image in enumerate(images) if TickWindows(image).hasTickMark()]
            return [tickField.locations[index].label for index in extractedIndices]

        # List out the tick mark with the given field and page number, pageNo starts from 0 and
        # configuration file has starting from 1.
        def extractTickMark(name, images):
            tickField = fieldTickMark(name, self.pageNo + 1)
            return [] if not tickField else extractTickLabel(tickField, images)

        return {fieldName: extractTickMark(fieldName, images) for (fieldName, images) in tickMarks}

    def __processOCRBatch(self, fieldSlices):

        def cleanStr(text, fieldName):
            match extractSemanticInfo(fieldName, self.pageNo + 1).availableCharacters:
                case 'alphabets':
                    return keepAlphabets([*text]).strip()
                case 'numbers':
                    return keepNumbers([*text]).strip()
                case _:
                    return text.strip()

        return {field: [cleanStr(text, field) for text in texts] for (field, texts) in ocrTextList(fieldSlices)}
