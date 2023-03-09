# Homography Extraction.

# Header utility.
import cv2
import numpy as np


class ImageHomography:
    # Default constructor takes source image and target image.
    # source and target both are color images.
    def __init__(self, sourceImage, inputImage):
        self.sourceImage = sourceImage
        self.inputImage = inputImage

    def transform(self):
        # Convert to grayscale.
        imgSource = cv2.cvtColor(self.sourceImage, cv2.COLOR_BGR2GRAY)
        imgInput = cv2.cvtColor(self.inputImage, cv2.COLOR_BGR2GRAY)
        height, width = imgSource.shape

        # Create ORB detector with 5000 features.
        orb_detector = cv2.ORB_create(5000)

        # Find key-points and descriptors.
        # The first arg is the image, second arg is the mask
        #  (which is not required in this case).
        kp1, d1 = orb_detector.detectAndCompute(imgInput, None)
        kp2, d2 = orb_detector.detectAndCompute(imgSource, None)

        # Match features between the two images.
        # We create a Brute Force matcher with
        # Hamming distance as measurement mode.
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match the two sets of descriptors.
        matches = matcher.match(d1, d2)

        # Take the top 90 % matches forward.
        matches = matches[:int(len(matches) * 0.9)]
        no_of_matches = len(matches)

        # Define empty matrices of shape no_of_matches * 2.
        p1 = np.zeros((no_of_matches, 2))
        p2 = np.zeros((no_of_matches, 2))

        for i in range(len(matches)):
            p1[i, :] = kp1[matches[i].queryIdx].pt
            p2[i, :] = kp2[matches[i].trainIdx].pt

        # Find the homography matrix.
        homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)

        # Use this matrix to transform the
        # colored image wrt the reference image.
        transformedImage = cv2.warpPerspective(self.inputImage, homography, (width, height))
        # transformedImage = cv2.cvtColor(transformedImage, cv2.COLOR_BGR2GRAY)

        return transformedImage
