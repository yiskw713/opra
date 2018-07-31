import os.path

import numpy as np
import cv2


def _resize_points(points, src_shape, dst_shape):
    """Resize the points."""
    xs = points[:, 0]
    ys = points[:, 1]
    new_xs = xs * dst_shape[0] / src_shape[0]
    new_ys = ys * dst_shape[1] / src_shape[1]
    new_points = np.hstack([new_xs[:, np.newaxis], new_ys[:, np.newaxis]])
    return new_points


class Dataset(object):

    def __init__(self,
                 data_dir,
                 annotation_path,
                 num_points=10):
        self._data_dir = data_dir
        self._num_points = num_points
        self._annotation_path = annotation_path

        self._data = self.load()
        self.resize_points()

    @ property
    def data_dir(self):
        return self._data_dir

    @ property
    def num_points(self):
        return self._num_points

    @property
    def data(self):
        return self._data

    def load(self):
        data = []

        with open(self._annotation_path, 'r') as fin:
            for line in fin:
                items = line.split(' ')

                points = []
                for i in xrange(self.num_points):
                    x = float(items[8 + 2 * i])
                    y = float(items[8 + 2 * i + 1])
                    points.append([x, y])

                points = np.array(points, dtype=np.float32)

                height = float(items[6])
                width = float(items[7])
                image_shape = (int(height), int(width))

                entry = {
                        'channel': items[0],
                        'playlist': items[1],
                        'video': items[2],
                        'start_time': items[3],
                        'duration': items[4],
                        'image': items[5],
                        'image_shape': image_shape,
                        'points': np.array(points, dtype=np.float32),
                        }

                data.append(entry)

        return data

    def resize_points(self):
        for index in range(len(self.data)):
            entry = self.data[index]
            image_path = self.get_image_path(index)
            im = cv2.imread(image_path)

            image_shape = entry['image_shape']
            if (im.shape[0] != image_shape[0]) or (
                    im.shape[1] != image_shape[1]):
                entry['points'] = _resize_points(
                        entry['points'], image_shape, im.shape)
                entry['image_shape'] = (im.shape[0], im.shape[1])

    def get_image_path(self, index):
        entry = self.data[index]

        image_name = os.path.join(
                entry['channel'], entry['playlist'], entry['video'],
                entry['image'])

        return os.path.join(self._data_dir, 'images', image_name)

    def get_video_path(self, index):
        entry = self.data[index]
        
        video_name = os.path.join(
                entry['channel'], entry['playlist'], entry['video'],
                '%s_%s.mp4' % (entry['start_time'], entry['duration']))

        return os.path.join(self._data_dir, 'clips',  video_name)