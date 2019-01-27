import numpy as np
import cv2
import h5py


class ImageLoader:
    def __init__(self, sample, target):
        self.sample = cv2.imread(sample, 0)
        self.target = cv2.imread(target, 0)

    def generateTrainingData(self):
        padded = np.pad(self.sample, (1,1), 'constant', constant_values=0)
        res = np.zeros((padded.shape[0] * padded.shape[1],10), dtype='uint8')
        elem_count = 0
        for x in range(1, padded.shape[0]-1):
            for y in range(1, padded.shape[1]-1):
                elem = np.empty(10, dtype='uint8')
                count = 0
                for i in range(x-1, x+2):
                    for j in range(y-1, y+2):
                        elem[count] = padded[i,j]
                        count += 1
                if self.target[x-1, y-1] == 255:
                    elem[9] = 1
                else:
                    elem[9] = 0
                res[elem_count] = elem
                elem_count += 1
        return res


if __name__ == "__main__":
    try:
        for num in range(0, 200):
            print('Processing image {} from table 1'.format(num))
            img1 = './target1/image_{}.png'.format(num)
            img2 = './target1/gbmask_np_{}.png'.format(num)
            if num == 0:
                data = ImageLoader(img1, img2).generateTrainingData()
            else:
                res = ImageLoader(img1, img2).generateTrainingData()
                data = np.vstack((data, res))

        with h5py.File("trainingset1.hdf5", "w") as f:
            dset = f.create_dataset("trainingset", data=data)
        print('Stored table 1')

        for num in range(0, 200):
            print('Processing image {} from table 2'.format(num))
            img1 = './target2/image_{}.png'.format(num)
            img2 = './target2/gbmask_{}.png'.format(num)
            if num == 0:
                data = ImageLoader(img1, img2).generateTrainingData()
            else:
                res = ImageLoader(img1, img2).generateTrainingData()
                data = np.vstack((data, res))

        with h5py.File("trainingset2.hdf5", "w") as f:
            dset = f.create_dataset("trainingset", data=data)
        print('Stored table 2')

        for num in range(0, 200):
            print('Processing image {} from table 3'.format(num))
            img1 = './target3/image_grad_{}.png'.format(num)
            img2 = './target3/gbmask_grad_{}.png'.format(num)
            if num == 0:
                data = ImageLoader(img1, img2).generateTrainingData()
            else:
                res = ImageLoader(img1, img2).generateTrainingData()
                data = np.vstack((data, res))

        with h5py.File("trainingset3.hdf5", "w") as f:
            dset = f.create_dataset("trainingset", data=data)
        print('Stored table 3')

    except Exception as e:
        print(e)
