import imageio.v3 as imageio
from imageio import imsave
import numpy as np
import random

_seed = 0xd8a6d669

def red_rows(img):
    for i in range(img.shape[0]):
        turn_red = random.uniform(0,1) <= 0.5

        for j in range(img.shape[1]):
            if turn_red:
                img[i][j][0] = 255
    return img

def _shift_row(img_row, shift):
    a = max(-shift,0)
    b = min(-shift,0)

    lpadding = np.repeat(img_row[:1], -b, axis=0)
    mshifted = img_row[a or None:b or None]
    rpadding = np.repeat(img_row[-1:], a, axis=0)

    if lpadding.size > 0:
        img_row = np.vstack((lpadding, mshifted))
    elif rpadding.size > 0:
        img_row = np.vstack((mshifted,rpadding))
    else:
        img_row = mshifted

    return img_row

def shift_rows(img,
               rate=0.3,
               max_scale=4, min_scale=1,
               leftrate=0.5,
               seed=_seed):
    random.seed(seed)
    for i in range(img.shape[0]):
        # r.v. for glitch probability
        U = random.uniform(0,1)
        if U <= rate:
            # magnitude of shift
            scale = random.randint(min_scale, max_scale)
            # side of shift
            U = random.uniform(0,1)
            side = (U <= leftrate) * 2 - 1

            img[i] = _shift_row(img[i], side*scale)
    return img
