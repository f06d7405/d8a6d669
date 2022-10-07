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

def _rgbize_pixel(pixel, rgb, damping=0.3, opacity=0.5):
    c = 1-damping
    match rgb:
        case "R":
            return [255, int(pixel[1] * c), int(pixel[2] * c), int(pixel[3] * opacity)]
        case "G":
            return [int(pixel[0] * c), 255, int(pixel[2] * c), int(pixel[3] * opacity)]
        case "B":
            return [int(pixel[0] * c), int(pixel[1] * c), 255, int(pixel[3] * opacity)]
        case _:
            raise ValueError

def _alpha_blend(px_above, px_below):
    a_a = px_above[3]/255
    a_b = px_below[3]/255
    a_o = a_a + a_b * (1 - a_a)
    if a_o == 0:
        return [0,0,0,0]
    px_o = [0,0,0,int(a_o*255)]
    for i in range(3):
        px_o[i] = int((px_above[i] * a_a + px_below[i] * a_b * (1 - a_a))/a_o)
    return px_o

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

def glitch_rows(img,
               rate=0.3,
               max_scale=5, min_scale=2,
               color_scale = 2,
               lcolor = "B", rcolor = "R",
               leftrate=0.5,
               seed=_seed):
    img = shift_rows(img, rate, max_scale, min_scale, leftrate, seed)
    limg = np.copy(img)
    rimg = np.copy(img)
    limg = shift_rows(limg, rate=1, max_scale=color_scale, min_scale=color_scale, leftrate=1)
    rimg = shift_rows(rimg, rate=1, max_scale=color_scale, min_scale=color_scale, leftrate=0)

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            limg[i][j] = _rgbize_pixel(limg[i][j], lcolor)
            rimg[i][j] = _rgbize_pixel(rimg[i][j], rcolor)
            img[i][j]  = _alpha_blend(img[i][j], limg[i][j])
            img[i][j]  = _alpha_blend(img[i][j], rimg[i][j])
    return img
