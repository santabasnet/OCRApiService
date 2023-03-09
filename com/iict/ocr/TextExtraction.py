# Text Extraction Utility.
import os
import cv2
import json
import numpy as np
from PIL import Image
import pytesseract
from werkzeug.utils import secure_filename

from com.iict.jsondata import BankForms
from com.iict.ocr import FileUtils, PagesExtraction
from com.iict.ocr.ImageProcessor import ImageProcessor
from com.iict.ocr.OCRApi import Document
from com.iict.ocr.PagesExtraction import AllPagesExtraction

imageDocument = None
templateImage = cv2.imread("assets/source.png", cv2.IMREAD_COLOR)
templateImages = BankForms.allTemplateImages()
custom_config = r'-l eng --oem 3 --psm 7'


# Perform OCR for an image slice, it is numpy array.
# which means, it is converted PIL image to perform
# OCR operation.
async def ocrTesseractText(image):
    # Perform resize operation.
    # Convert numpy image to PIL image to perform OCR.
    newImage = Image.fromarray(np.uint8(image)).convert('RGB')
    return pytesseract.image_to_string(newImage, config=custom_config)


# Execute OCR operation for all the image slices.
async def extractSlices(imageSlices):
    return {name: await PagesExtraction.ocrText(image) for (name, image) in imageSlices.items()}


# Execute OCR operation for all the image slices.
async def extractSlicesWithTesseract(imageSlices):
    return {name: await ocrTesseractText(image) for (name, image) in imageSlices.items()}


# Perform image alignment and then slice them according to the
# template definition.
async def imageAlignment(inputImage):
    return PagesExtraction.imageAlignment(templateImage, inputImage)


# Process and extract input image.
async def processInputImage(inputImage):
    imageSlices = await imageAlignment(inputImage)
    outputFields = await extractSlices(imageSlices)
    return json.dumps(outputFields, indent=4)


# Process all the images extracted from the pdf file.
async def processInputImages(allInputImages):
    return AllPagesExtraction(allInputImages).alignAndExtractImages()


# Process and extract input image with tesseract OCR.
async def processImageWithTesseract(inputImage):
    # imageSlices = await imageAlignment(inputImage)
    # outputFields = await extractSlicesWithTesseract(imageSlices)
    outputFields = AllPagesExtraction.alignPage(templateImage, inputImage)
    return json.dumps(outputFields, indent=4)


# Save and Start processing here.
async def saveAndProcess(inputFile):
    fileName = secure_filename(inputFile.filename)
    filePath = os.path.join(FileUtils.UPLOAD_FOLDER, fileName)
    inputFile.save(filePath)
    # inputImage = cv2.imread(filePath, cv2.IMREAD_COLOR)
    # return await processInputImage(inputImage)

    # Load list of all the images from the pdf.
    allInputImages = FileUtils.extractImages(filePath)
    return await processInputImages(allInputImages)


# Extract from the static file.
async def staticProcess():
    inputImage = cv2.imread("assets/target.png", cv2.IMREAD_COLOR)
    return await processInputImage(inputImage)


# Extract text with Tesseract OCR.
async def tesseractProcess(inputFile):
    fileName = secure_filename(inputFile.filename)
    filePath = os.path.join(FileUtils.UPLOAD_FOLDER, fileName)
    inputFile.save(filePath)
    inputImage = cv2.imread(filePath, cv2.IMREAD_COLOR)
    return await processImageWithTesseract(inputImage)
