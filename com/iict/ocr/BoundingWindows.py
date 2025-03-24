# Importing all the required modules
import cv2
import numpy as np
import random as rng


# Object-oriented design for the large bounding box ocr region.
class BoundingWindows:
    # Default constructor.
    def __init__(self, _bgrImage):
        self._totalAreaFactor = _bgrImage.shape[0] * _bgrImage.shape[1] * 0.95
        self._bgrImage = _bgrImage
        self._contours = self.__findContours()

    # Determine the interested region for the given rectangle.
    def interestedRegion(self):
        return self.__extremePoints()

    # Determine all the contours.
    def __findContours(self):
        ret, thresh = cv2.threshold(self._bgrImage, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        return self.__filterBoxes(contours)

    # Estimate average parameters.
    def __averageWidthHeight(self):
        totalHeight = 0.0
        totalWidth = 0.0
        for box in self._contours:
            _, _, w, h = cv2.boundingRect(box)
            totalHeight = totalHeight + h
            totalWidth = totalWidth + w
        count = len(self._contours)
        return totalWidth / count, totalHeight / count

    # Factors for width and height.
    def __widthHeightFactor(self):
        fWidth, fHeight = self.__averageWidthHeight()
        return fWidth * 0.50, fHeight * 0.50

    # Boundary condition for the bounding box to be a valid box.
    def __isInterested(self, box):
        x, y, w, h = cv2.boundingRect(box)
        return w >= 8 and h >= 8 and (w * h) < self._totalAreaFactor

    # Select interested contours only. (Remove smaller and larger ones)
    def __filterBoxes(self, contours):
        return [b for b in contours if self.__isInterested(b)]

    # Estimate extreme top left and right bottom points for the region.
    def __extremePoints(self):
        if len(self._contours) < 1:
            return 0, 0, 0, 0
        else:
            minX = 3000
            minY = 2000
            maxX = 0
            maxY = 0
            for box in self._contours:
                x, y, w, h = cv2.boundingRect(box)
                x2 = x + w
                y2 = y + h
                minX = x if x < minX else minX
                minY = y if y < minY else minY
                maxX = x2 if x2 > maxX else maxX
                maxY = y2 if y2 > maxY else maxY
            return minX, minY, maxX, maxY

    # Filtered Boxes.
    def interestedBoxes(self):
        return self._contours

    # Check if the image has enough boxes for the OCR or not.
    # There must be some number of boxes.
    def hasMinimumBoxes(self):
        return len(self._contours) > 1

    # Cropped Image.
    def croppedImage(self):
        x1, y1, x2, y2 = self.__extremePoints()
        return self._bgrImage[y1:y2, x1:x2]


# Utility for tick-mark.
class TickWindows:
    # Default constructor.
    def __init__(self, _bgrImage):
        self._padding = 3
        self._height = _bgrImage.shape[0] + (2 * self._padding)
        self._width = _bgrImage.shape[1] + (2 * self._padding)
        self._totalAreaFactor = self._width * self._height * 0.98
        self._bgrImage = _bgrImage
        self._contours = self.__findContours()

    # Check if the bounding box has the same image size.
    def __hasSameBox(self, box):
        _, _, w, h = cv2.boundingRect(box)
        return w == self._width and h == self._height

    # Determine all the contours.
    def __findContours(self):
        image = cv2.copyMakeBorder(self._bgrImage, 3, 3, 3, 3, cv2.BORDER_CONSTANT, None, value=255)
        ret, thresh = cv2.threshold(image, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return [c for c in contours if not self.__hasSameBox(c)]

    # Area constraint.
    def __areaValidity(self, w, h):
        return float(w * h) <= self._totalAreaFactor

    # Dimension constraint: 30% of height and width.
    def __dimValidity(self, w, h):
        return float(w) >= float(self._width) * 0.30 and float(h) >= float(self._height) * 0.30

    # Validate if the contours contains the 25% of height and width.
    def __hasValidContour(self, box):
        _, _, w, h = cv2.boundingRect(box)
        return self.__dimValidity(w, h) and self.__areaValidity(w, h)

    # Utility for the bounding boxes.
    def hasTickMark(self):
        allBoxes = [contour for contour in self._contours if self.__hasValidContour(contour)]
        return not allBoxes == []
