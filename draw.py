import matplotlib.pyplot as plt
import matplotlib.image as mpl_image
from matplotlib.patches import Polygon
import matplotlib.patheffects as PathEffects
import numpy as np


def prepare(background_image_filename, draw=True):
    image = mpl_image.imread(background_image_filename)
    plt.close(plt.gcf())
    plt.figure(figsize=(image.shape[1] / 100, image.shape[0] / 100))
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    if draw:
        plt.imshow(image)
    plt.axis("off")
    plt.xlim([0, image.shape[1]])
    plt.ylim([image.shape[0], 0])


def point(*args, **kwargs):
    plt.scatter(*args, **kwargs)


def circle(*args, **kwargs):
    ax = plt.gca()
    ax.add_artist(plt.Circle(*args, **kwargs))


def line(x1, y1, x2, y2, *args, **kwargs):
    plt.plot([x1, x2], [y1, y2], *args, **kwargs)


def polygons(polygons_data_list, *args, **kwargs):
    for polygon_data in polygons_data_list:
        pol = Polygon(polygon_data, *args, **kwargs)
        plt.gca().add_patch(pol)


def text(*args, effects=None, **kwargs):
    txt = plt.text(*args, **kwargs)
    if effects is not None:
        txt.set_path_effects([PathEffects.withStroke(**effects)])


def offset(x, y, o):
    """ Offset coordinates given by array x,y by o """
    X = np.c_[x, y].T
    m = np.array([[0, -1], [1, 0]])
    R = np.zeros_like(X)
    S = X[:, 2:] - X[:, :-2]
    R[:, 1:-1] = np.dot(m, S)
    R[:, 0] = np.dot(m, X[:, 1] - X[:, 0])
    R[:, -1] = np.dot(m, X[:, -1] - X[:, -2])
    On = R / np.sqrt(R[0, :] ** 2 + R[1, :] ** 2) * o
    Out = On + X
    return Out[0, :], Out[1, :]


def offset_curve(x, y, o):
    """ Offset array x,y in data coordinates
        by o in points """
    ax = plt.gca()
    trans = ax.transData.transform
    inv = ax.transData.inverted().transform
    X = np.c_[x, y]
    Xt = trans(X)
    xto, yto = offset(Xt[:, 0], Xt[:, 1], o * 100 / 72.)
    Xto = np.c_[xto, yto]
    Xo = inv(Xto)
    return Xo[:, 0], Xo[:, 1]


def save_as(*args, **kwargs):
    plt.savefig(*args, **kwargs)


def show():
    plt.show()
