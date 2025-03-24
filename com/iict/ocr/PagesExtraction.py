# Class definition for the extracted pdf images and process them page by page.
# It accumulates the response in Json formate page-wise.
import cv2
import json
import numpy as np
from PIL import Image
from itertools import islice
from multiprocessing import Process

from com.iict.jsondata import BankForms
from com.iict.ocr.FieldExtraction import FieldExtraction, DOCUMENT_MODEL, BatchExtraction
from com.iict.ocr.ImageProcessor import ImageProcessor
from com.iict.ocr.OCRApi import Document

# A global variable for controlling the Number of pages.
NUMBER_OF_PAGES = 2


# Interpolation method
def interpolationMethod(image, width):
    h, w = image.shape[:2]
    if w > width:  # image is shrinking
        return cv2.INTER_AREA
    else:  # image is now enlarged.
        return cv2.INTER_CUBIC


# Perform image resize keeping aspect ratio same.
def imageResize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


# Perform OCR for an image slice, it is numpy array.
# which means, it is converted PIL image to perform
# OCR operation.
def _ocrText(image, pageNo):
    # Assign new width,
    # newWidth = 320
    # Perform image resize.
    # resizedImage = imageResize(image, width=newWidth, inter=interpolationMethod(image, newWidth))

    # Convert numpy image to PIL image to perform OCR.
    newImage = Image.fromarray(np.uint8(image)).convert('RGB')
    return "" if newImage.size == (0, 0) else DOCUMENT_MODEL.extract(newImage)


# Execute OCR operation for all the image slices.
# Returns the dictionary of field name and OCR output.
def extractSlices(imageSlices, pageNo):
    # OCR done one image at a time.
    # fieldResults = {name: FieldExtraction(pageNo, name, images).extract() for (name, images) in imageSlices.items()}
    # return fieldResults
    def chunks(data, SIZE=20):
        it = iter(data)
        for i in range(0, len(data), SIZE):
            yield {k: data[k] for k in islice(it, SIZE)}

    # Process batch fields for the page OCR.
    # 12 for number of images in batch OCR.
    batchSlices = chunks(imageSlices, 12)
    # Display batch sizes.
    # for batch in batchSlices:
    #     print(len(batch))
    # print("\n")

    batchResults = [BatchExtraction(pageNo, batch).extract() for batch in batchSlices]
    # Needs to merge the list of dictionaries.
    finalResults = {k: v for x in batchResults for k, v in x.items()}

    return finalResults


# Returns the list of slices, a list of sliced image.
def imageAlignment(_templateImage, _inputImage, pageNo):
    return ImageProcessor(_templateImage, _inputImage) \
        .findHomoGraphy() \
        .getDifference() \
        .sliceOCRAreas(pageNo)


class AllPagesExtraction:
    # inputImages represents the dictionary constructed with the page and
    # its associated image.
    def __init__(self, _inputImages):
        # input images are of page with their values.
        self._inputImages = _inputImages

    # Get the input image with the given page number.
    def __inputImageOf(self, noOfPages):
        return {page: self._inputImages[page] for page in range(noOfPages)}

    # Perform image alignment and then slice them according to the
    # template definition.
    @classmethod
    def alignPage(cls, _templateImage, _inputImage, pageNo):
        # Images extraction is working now.
        # path1 = f"assets/output/Source_{pageNo}.png"
        # cv2.imwrite(path1, _templateImage)
        # path2 = f"assets/output/Target_{pageNo}.png"
        # cv2.imwrite(path2, _inputImage)

        # Returns the dictionary of image slices of field name and associated image.
        imageSlices = imageAlignment(_templateImage, _inputImage, pageNo)

        # for (fieldName, images) in imageSlices.items():
        #     path = f"assets/output/{fieldName}_{pageNo}.png"
        #     print(type(images[0]))
        #
        #     if images[0]:
        #         cv2.imwrite(path, images[0])
        #
        # print("Slices of : " + str(pageNo))
        # print(imageSlices)

        # Returns the dictionary of field name and the extracted text.
        outputFields = extractSlices(imageSlices, pageNo)
        return outputFields

    # Combine both align and extract operation here.
    def alignAndExtractImages(self):
        # All images are in the list.
        allTemplates = BankForms.allTemplateImages()
        outBound = 2  # len(allTemplates)
        templateImages = {pageIndex: allTemplates[pageIndex] for pageIndex in range(outBound)}

        # uploadedImages = {
        #    pageIndex: self._inputImages[pageIndex].shape for (pageIndex, image) in self._inputImages.items()
        # }

        extractedFields = {
            page: AllPagesExtraction.alignPage(templateImages[page], inputImage, page) for
            (page, inputImage) in self.__inputImageOf(outBound).items()
        }

        print("\nResult: ")
        print(extractedFields)

        return json.dumps(extractedFields, indent=4)
