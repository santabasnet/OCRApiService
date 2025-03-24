# Image processor, pre-processing operations are defined here.
import cv2

from com.iict.jsondata.BankForms import FormField
from com.iict.ocr import DocumentFields
from com.iict.ocr.BoundingWindows import BoundingWindows
from com.iict.ocr.Homography import ImageHomography


class ImageProcessor:
    # Default constructor for source i.e. template image and
    # the input image.
    def __init__(self, sourceImage, inputImage):
        self.sourceImage = sourceImage
        self.inputImage = inputImage
        self.transformedImage = None
        self.diffImage = None

    def findHomoGraphy(self):
        homography = ImageHomography(self.sourceImage, self.inputImage)
        self.transformedImage = homography.transform()
        return self

    def getDifference(self):
        sourceGrayImage = cv2.cvtColor(self.sourceImage, cv2.COLOR_BGR2GRAY)
        transformedGrayImage = cv2.cvtColor(self.transformedImage, cv2.COLOR_BGR2GRAY)
        self.diffImage = 255 - cv2.absdiff(sourceGrayImage, transformedGrayImage)
        _, self.diffImage = cv2.threshold(self.diffImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return self

    def __makeSlice(self, location):
        x1, y1 = location.topLeft.point()
        x2, y2 = location.bottomRight.point()
        # print(f'(x1 = {x1}, y1 = {y1}) and (x2 = {x2}, y2 = {y2}) Image size : {self.diffImage.shape}')
        givenSlice = self.diffImage[y1:y2, x1:x2]
        # return BoundingWindows(givenSlice).croppedImage()
        return givenSlice

    def __makeSlices(self, formField, pageNo):
        results = [self.__makeSlice(location) for location in formField.locations]
        # Temporarily save the sliced image.
        for i in range(len(results)):
            path = f'assets/output/{formField.getName()}_{pageNo}_{i}.png'
            cv2.imwrite(path, results[i])
        return results

    # Returns the dictionary of form field
    def sliceOCRAreas(self, pageNo) -> dict[str, list]:
        ocrFields: list[FormField] = DocumentFields.ocrFromTemplateFields(pageNo + 1)
        return {formField.getName(): self.__makeSlices(formField, pageNo) for formField in ocrFields}
