# File Utility codes are placed here.

# Extract Pages from pdf.
# Libraries
import fitz
import io
from PIL import Image
import cv2
import numpy as np

# File type definition: all the possible types.
ALL_SUPPORTED_TYPES = ['JPEG', 'PNG', 'PDF']

# Uploads folder.
UPLOAD_FOLDER = 'assets/uploads/'

# Slices Path.
SLICES_FOLDER = 'assets/output/'

# Templates Folder.
TEMPLATES_FOLDER = 'assets/templates/'


# Checks if the uploaded file is of valid format or not.
def isValid(inputFile):
    return '.' in inputFile.filename and inputFile.filename.rsplit('.', 1)[1].upper() in ALL_SUPPORTED_TYPES


# Extract base image.
def baseImageOf(pdfFile, image):
    return pdfFile.extract_image(image[0])


# Extract extension for the image.
def imageExtension(image):
    return baseImageOf(image)['ext']


# Extract image bytes content.
def imageContent(pdfFile, image):
    return io.BytesIO(baseImageOf(pdfFile, image)['image'])


# Image Name.
def imageNameOf(image):
    return image[7]


# Convert CV image from PIL image.
def cvImageOf(pilImage):
    return cv2.cvtColor(np.array(pilImage), cv2.COLOR_RGB2BGR)


# Perform Image extraction from the pdf file.
# Especially, it assumes content of single image per page.
# It returns dictionary of page number and the image associated with it.
def extractImages(pdfFileName):
    # Open PDF file
    pdfFile = fitz.open(pdfFileName)

    # Calculate number of pages in PDF file and Extract images and group them in page index
    # and select the first one hoping that single page has an image only.
    pageWithImage = {page: pdfFile[page].get_images()[0] for page in range(len(pdfFile))}

    # Content of page number with images.
    pageIndexWithImage = {page: Image.open(imageContent(pdfFile, content)) for (page, content) in pageWithImage.items()}

    # Convert PIL image to open CV image.
    pageWithCVImage = {page: cvImageOf(image) for (page, image) in pageIndexWithImage.items()}

    # Validate how many images are in each page.
    # imageSizes = {page: len(content) for (page, content) in images.items()}
    return pageWithCVImage


# Read Image File from OpenCV.
def readImage(fileName):
    image = cv2.imread(fileName, cv2.IMREAD_COLOR)
    return image
