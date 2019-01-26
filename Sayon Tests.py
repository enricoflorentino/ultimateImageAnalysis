# Target 1: Measure the fraction of the dark phase with an accuracy of 0.5%
#           or better in an image that does not contain particles
#           (e.g. micro1.png).

# Target 2: Measure the fraction of the dark phase with an accuracy of 0.5%
#           or better in an image that contains particles (e.g. micro3.png).
#           For images with particles, the particles inside the dark phase
#           should be counted with the dark phase and the ones inside the
#           light phase should be counted with the light phase.

# Target 3: Same as target 2, but you will be given images with uneven
#           lighting conditions.

# Target 4: You need to measure the average size (equivalent diameter)
#           of the grains in the images. The “grains” simply refer to the
#           polygons that make the images.

# Target 5: You are able to produce a histogram of the grain size.

import cv2
import numpy as np
import os


class GrainPic:

    def __init__(self, path, threshold=False, grain_boundaries=None):
        self.img = cv2.imread(path, 0)
        self.grain_boundaries = grain_boundaries
        if threshold:
            self.grain_boundaries = self.find_grain_boundaries()
            _, img = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

            # Opening
            kernel = np.ones((2, 2), np.uint8)
            img = cv2.erode(img, kernel, iterations=6)
            self.img = cv2.dilate(img, kernel, iterations=2)

        # indices = self.grain_boundaries.astype(np.uint8)  #convert to an unsigned byte
        # indices *= 255
        # cv2.imshow('Indices', indices)
        # cv2.waitKey()
        self.size = self.img.shape
        self.num_pixels = self.size[0]*self.size[1]
        self.whites = np.sum(self.img == 0)
        self.darks = np.sum(self.img == 255)

        # ignore grain_boundaries
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.grain_boundaries[i][j]:
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

    def find_grain_boundaries(self):
        img = cv2.Canny(self.img, 30, 60)
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(img, kernel, iterations=2)
        self.canny_img = cv2.erode(img, kernel, iterations=2)
        grain_boundaries = (self.canny_img == 255)
        return grain_boundaries

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

    def __repr__(self):
        return str(self.img)


folder_path = '/home/sayon/Documents/Datasets/Materials Micrographs/Target 1'
errors = []
count = 0

# for i in range(200):
#     attempt_path = os.path.join(folder_path, 'image_'+str(i)+'.png')
#     answer_path = os.path.join(folder_path, 'p1mask_np_'+str(i)+'.png')
#     attempt = GrainPic(attempt_path, threshold=True)
#     answer = GrainPic(answer_path, ignores=attempt.ignores)
#     errors.append(attempt.error(answer))
#     if attempt.error(answer) > 0.5:
#         print(f'{attempt_path}: {attempt.error(answer)}')
#         count += 1
# print(count)
# print('min: {minimum}')
# print('max: {minimum}')

attempt_path = '/home/sayon/Documents/Datasets/Materials Micrographs/Target 1/image_0.png'
test_path = '/home/sayon/Documents/Datasets/Materials Micrographs/Target 1/p1mask_np_0.png'

attempt = GrainPic(attempt_path, threshold=True)
test = GrainPic(test_path, grain_boundaries=attempt.grain_boundaries)
attempt.show()
# print(test)
# print(attempt)
# print(test.darks)
# print(attempt.darks)
# print(attempt.fraction_of_darks)
# print(test.fraction_of_darks)
print(attempt.error(test))
print(attempt.show_difference(test))
