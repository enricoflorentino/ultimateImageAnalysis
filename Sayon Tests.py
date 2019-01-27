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
import scipy.ndimage as ndi
from statistics import median
from copy import deepcopy
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(color_codes=True)
class Grain:
    def __init__(self, grain_contour, img, threshold):
        self.img = deepcopy(img)
        self.area = cv2.contourArea(grain_contour)
        self.equivalent_diameter = np.sqrt(4*self.area/np.pi)
        x, y, w, h = cv2.boundingRect(grain_contour)
        cv2.fillPoly(self.img, [grain_contour], color=(0, 0, 255))
        points = []
        for i in range(x, x+w):
            for j in range(y, y+h):
                inside = cv2.pointPolygonTest(grain_contour, (i, j), False)
                if inside >= 0:
                    points.append((i, j))
        self.threshold = threshold
        intensities = 0
        for point in points:
            intensities += img[point[1]][point[0]]
        self.average_intensity = intensities/len(points)

        if self.average_intensity <= self.threshold:
            self.color = 'dark'
        else:
            self.color = 'white'
        # print(self.average_intensity)
        # print(self.color)
        show(self.img)


class GrainPic:
    def __init__(self, path, threshold=False, grain_boundary_path=None):
        self.img = cv2.imread(path, 0)
        self.size = self.img.shape
        self.num_pixels = self.size[0]*self.size[1]
        if threshold:
            self.grain_boundaries = self.find_grain_boundaries()
            self.thresh = cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY,11, 1)
            show(self.img)
            show(self.thresh)
            limit, _ = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            # kernel = np.ones((2, 2), np.uint8)
            # thresh = cv2.erode(thresh, kernel, iterations=4)
            # thresh = cv2.dilate(thresh, kernel, iterations=4)
            # show(img2)
            contours, hierarchy = cv2.findContours(self.thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            self.grains = []
            for contour in contours:
                if cv2.contourArea(contour) > 700:
                    self.grains.append(Grain(contour, self.img, limit))

            self.whites = sum([grain.area for grain in self.grains if grain.color == 'white'])
            self.darks = sum([grain.area for grain in self.grains if grain.color == 'dark'])
            self.grain_sizes = [grain.equivalent_diameter for grain in self.grains]
            # Opening
            # self.img = cv2.erode(self.img, kernel, iterations=2)
            # self.img = cv2.dilate(self.img, kernel, iterations=1)
            # self.img = cv2.erode(self.img, kernel, iterations=2)
            # self.img = cv2.dilate(self.img, kernel, iterations=2)
            # kernel = np.ones((2, 1), np.uint8)
            # self.img = cv2.erode(self.img, kernel, iterations=9)
            # self.img = cv2.dilate(self.img, kernel, iterations=5)
            # self.img = cv2.erode(self.img, kernel, iterations=6)
            # self.img = cv2.dilate(self.img, kernel, iterations=7)
            # ignore grain_boundaries
            # self.whites = np.sum(np.logical_and(img2 == 0, self.grain_boundaries == False))
            # self.darks = np.sum(np.logical_and(img2 == 255, self.grain_boundaries == False))
        else:
            self.grain_boundaries = cv2.imread(grain_boundary_path, 0)
            # self.whites = np.sum(self.img == 0)
            # self.darks = np.sum(self.img == 255)
            self.whites = np.sum(np.logical_and(self.img == 0, self.grain_boundaries == 0))
            self.darks = np.sum(np.logical_and(self.img == 255, self.grain_boundaries == 0))
        self.fraction_of_darks = self.darks/self.num_pixels
    def find_grain_boundaries(self):
        grain_boundaries = cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY,11,2)
        _, grain_boundaries = cv2.threshold(grain_boundaries, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        grain_boundaries = cv2.erode(grain_boundaries, kernel, iterations=2)
        # grain_boundaries = cv2.dilate(grain_boundaries, kernel, iterations=4)
        grain_boundaries = (grain_boundaries == 255)
        grain_boundaries = np.zeros([1024, 1024], dtype=bool)
        return grain_boundaries
    def error(self, answer_pic):
        difference = abs(self.fraction_of_darks-answer_pic.fraction_of_darks)
        return (difference/answer_pic.fraction_of_darks)*100
    def compare(self, other_pic):
        return ((np.sum(self.img == other_pic.img))/self.num_pixels)*100
    def show_difference(self, answer_pic):
        img = self.img - answer_pic.img
        # for i in range(img.shape[0]):
        #     for j in range(img.shape[1]):
        #         if self.grain_boundaries[i][j]:
        #             img[i][j] -= 255
        img = cv2.resize(img, None, fx=0.5, fy=0.5,
                         interpolation=cv2.INTER_CUBIC)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    def make_histogram(self):
        sns.distplot(self.grain_sizes)
        plt.show()
    def __repr__(self):
        return str(self.img)


def show(image=None):
    if image is not None:
        if image.dtype == bool:
            image = image.astype('uint8')
            image *= 255
    image = cv2.resize(image, None, fx=0.5, fy=0.5,
                       interpolation=cv2.INTER_CUBIC)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
folder_path = '/home/sayon/Documents/Datasets/Materials Micrographs'
folder = 'Target 1'
folder_path = os.path.join(folder_path, folder)

def check_all():
    count = 0
    errors = []
    for i in range(200):
        attempt_path = os.path.join(folder_path, 'image_'+str(i)+'.png')
        answer_path = os.path.join(folder_path, 'p1mask_np_'+str(i)+'.png')
        if folder == 'Target 3':
            attempt_path = os.path.join(folder_path, 'image_grad_'+str(i)+'.png')
            answer_path = os.path.join(folder_path, 'p1mask_grad_'+str(i)+'.png')
        attempt = GrainPic(attempt_path, threshold=True)
        answer = GrainPic(answer_path, grain_boundary_path=boundary_path)
        errors.append(attempt.error(answer))
        if attempt.error(answer) > 0.5:
            print(f'{attempt_path}: {attempt.error(answer)}')
            count += 1
    print(count)
    print(f'mean:{sum(errors)/len(errors)}')
    print(f'median:{median(errors)}')

def check_image(image_num=0):
    attempt_path = r'C:\Users\enric\Desktop\realmicro.png'
    attempt = GrainPic(attempt_path, threshold=True)
    print(attempt.fraction_of_darks)

check_image()