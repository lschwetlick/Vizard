import numpy as np


# def kaleidoscope_basic(img, flipped=False):
#     w, h, _ = img.shape
#     img_t = np.rot90(img)
#     if flipped:
#         mask = np.expand_dims(np.tril(np.ones((w, h))).astype(int), 2)
#     else:
#         mask = np.expand_dims(np.triu(np.ones((w, h))).astype(int), 2)
#     comp = np.where(mask, img, img_t)
#     mirror = np.flip(comp, 1)
#     top = np.hstack((comp, mirror))
#     bottom = np.flip(top, 0)
#     kaleidoscope = np.vstack((top, bottom))
#     return kaleidoscope


def kaleidoscope_basic(img, flipped=0):
    w, h, _ = img.shape
    img_t = np.rot90(img)
    mask = np.triu(np.ones((w, h))).astype(int)
    if flipped == 0:
        fmask = np.expand_dims(mask, 2)
    if flipped == 1:
        fmask = np.stack([mask.T, mask, mask], axis=2)
    if flipped == 2:
        fmask = np.stack([mask, mask.T, mask], axis=2)
    if flipped == 3:
        fmask = np.stack([mask, mask, mask.T], axis=2)
    if flipped == 4:
        fmask = np.stack([mask.T, mask.T, mask], axis=2)
    if flipped == 5:
        fmask = np.stack([mask.T, mask, mask.T], axis=2)
    if flipped == 6:
        fmask = np.stack([mask, mask.T, mask.T], axis=2)
    if flipped == 7:
        fmask = fmask = np.expand_dims(mask.T, 2)

    comp = np.where(fmask, img, img_t)
    mirror = np.flip(comp, 1)
    top = np.hstack((comp, mirror))
    bottom = np.flip(top, 0)
    kaleidoscope = np.vstack((top, bottom))
    return kaleidoscope



def kaleidoscope_levels(img, n_segments, flipped=0, alternate_flip=False):
    #print("level", level)
    for _ in range(n_segments):
        img = img[::2, ::2, :]
        img = kaleidoscope_basic(img, flipped=flipped)
    return img


def multiscope(img, n_segments=2, flipped=0, alternate_flip=0):
    if n_segments == 0:
        return img
    w, h, _ = img.shape
    di = int(w / n_segments)
    segments = (np.arange(n_segments + 1) * di).astype(int)
    cnt = 0
    for i in range(1, n_segments + 1):
        for j in range(1, n_segments + 1):
            
            if cnt % 2 == 0:
                thisflip = flipped
            else:
                thisflip = alternate_flip
            if di % 2 != 0:
                img[segments[i - 1]:segments[i], segments[j - 1]:segments[j], :] = kaleidoscope_basic(img[segments[i - 1]:segments[i], segments[j - 1]:segments[j], :], flipped=thisflip)[::2, ::2, :]
            else:
                img[segments[i - 1]:segments[i], segments[j - 1]:segments[j], :] = kaleidoscope_basic(img[segments[i - 1]:segments[i]:2, segments[j - 1]:segments[j]:2, :], flipped=thisflip)
            cnt += 1
    return img


# make one knob me the number of channels that are flipped
# make a different knob be how much of the image is being kaleidoscoped
# make another knob be wether its one flipped one normal or all flipped and mirrored






