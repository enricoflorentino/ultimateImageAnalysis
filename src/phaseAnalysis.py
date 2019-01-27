import cv2
import numpy as np
import os


class GrainPic:

    def __init__(self, path, threshold=False, ignores=None):
        self.img = cv2.imread(path, 0)
        self.ignores = ignores
        if threshold:
            self.ignores = self.set_ignores()
            _, img = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            kernel = np.ones((2, 2), np.uint8)
            img = cv2.erode(img, kernel, iterations=6)
            self.img = cv2.dilate(img, kernel, iterations=2)

        self.size = self.img.shape
        self.num_pixels = self.size[0]*self.size[1]
        self.whites = np.sum(self.img == 0)
        self.darks = np.sum(self.img == 255)
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.ignores[i][j]:
                    if self.img[i][j] == 0:
                        self.whites -= 1
                    else:
                        self.darks -= 1

        self.fraction_of_darks = self.darks/self.num_pixels

    def show(self, image=None):
        img = self.img
        if image is not None:
            img = image
        img = cv2.resize(img, None, fx=0.5, fy=0.5,
                         interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def set_ignores(self):
        img = cv2.Canny(self.img, 30, 60)
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(img, kernel, iterations=2)
        self.canny_img = cv2.erode(img, kernel, iterations=2)
        to_ignore = (self.canny_img == 255)
        return to_ignore

    def error(self, answer_pic):
        difference = abs(self.fraction_of_darks-answer_pic.fraction_of_darks)
        return (difference/answer_pic.fraction_of_darks)*100

    def show_difference(self, answer_pic):
        img = self.img - answer_pic.img
        img = cv2.resize(img, None, fx=0.5, fy=0.5,
                         interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_dark_fraction(self):
        return self.fraction_of_darks

    def __repr__(self):
        return str(self.img)
