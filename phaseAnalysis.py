import cv2
import numpy as np
import os


class GrainPic:

    def __init__(self, path, threshold=False):
        self.img = cv2.imread(path, 0)
        self.size = self.img.shape
        self.num_pixels = self.size[0]*self.size[1]
        if threshold:
            _, img = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            kernel = np.ones((2, 2), np.uint8)
            img = cv2.erode(img, kernel, iterations=6)
            self.img = cv2.dilate(img, kernel, iterations=2)

        self.whites = np.sum(self.img == 0)
        self.darks = np.sum(self.img == 255)

        self.fraction_of_darks = round(self.darks/self.num_pixels, 3)

    def error(self, answer_pic):
        difference = abs(self.fraction_of_darks-answer_pic.fraction_of_darks)
        return (difference/answer_pic.fraction_of_darks)*100

    def __repr__(self):
        return str(self.img)