import json
import os
from copy import deepcopy
import seaborn as sns
import matplotlib.pyplot as plt 

import cv2
import numpy as np
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from phaseAnalysis import GrainPic

import matplotlib
matplotlib.use('Agg')

sns.set(color_codes=True);

app = Flask(__name__)
app.config['UPLOAD FOLDER'] = r'C:\Users\enric\Desktop'
CORS(app)


@app.route('/', methods=['GET'])
def process():
    if request.method == 'GET':
        input_data = dict(request.args)

        # If there is no input data, send the index.html
        if input_data == {}:
            return app.send_static_file('index.html')


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


class AdaptiveThreshold:

    def __init__(self, path, threshold=False):
        self.img = cv2.imread(path, 0)
        self.size = self.img.shape
        self.num_pixels = self.size[0]*self.size[1]
        if threshold:
            self.grain_boundaries = self.find_grain_boundaries()
            thresh = cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY,11, 1)
            limit, _ = cv2.threshold(self.img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            self.grains = []
            for contour in contours:
                if cv2.contourArea(contour) > 700:
                    self.grains.append(Grain(contour, self.img, limit))

            self.whites = sum([grain.area for grain in self.grains if grain.color == 'white'])
            self.darks = sum([grain.area for grain in self.grains if grain.color == 'dark'])
            self.grain_sizes = [grain.equivalent_diameter for grain in self.grains]
        else:
            self.grain_boundaries = cv2.imread(grain_boundary_path, 0)
            self.whites = np.sum(np.logical_and(self.img == 0, self.grain_boundaries == 0))
            self.darks = np.sum(np.logical_and(self.img == 255, self.grain_boundaries == 0))

        self.fraction_of_darks = self.darks/self.num_pixels

    def find_grain_boundaries(self):
        grain_boundaries = cv2.adaptiveThreshold(self.img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                cv2.THRESH_BINARY,11,2)
        _, grain_boundaries = cv2.threshold(grain_boundaries, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        grain_boundaries = cv2.erode(grain_boundaries, kernel, iterations=2)

        grain_boundaries = (grain_boundaries == 255)
        grain_boundaries = np.zeros([1024, 1024], dtype=bool)
        return grain_boundaries

    def error(self, answer_pic):
        difference = abs(self.fraction_of_darks-answer_pic.fraction_of_darks)
        return (difference/answer_pic.fraction_of_darks)*100

    def compare(self, other_pic):
        return ((np.sum(self.img == other_pic.img))/self.num_pixels)*100

    def make_histogram(self):
        plt.hist(self.grain_sizes)
        plt.title('Grain Sizes Histogram')
        plt.xlabel('Grain Size (Equivalent Diameter in Pixels)')
        plt.ylabel('Frequency')
        plt.savefig('static\Figure_1.png')
        plt.close()

    def __repr__(self):
        return str(self.img)
    
@app.route('/uploaded', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file'];      
        file.save(file.filename);     
        test = GrainPic(file.filename, True);
        for_hist = AdaptiveThreshold(file.filename, True);
        result = [];
        result.append(f'{test.fraction_of_darks*100}%');

        hist = for_hist.make_histogram()
        filename = 'static\Figure_1.png'
        return render_template('update.html',result=result, user_image=filename);

if __name__ == '__main__':
    app.run(debug=True)