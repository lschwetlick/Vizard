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

# def kaleidoscope_basic_slower(img, flipped=0):
#     w, h, _ = img.shape
#     kaleidoscope = np.empty((w*2,h*2,3), dtype=np.float32)
#     img_t = np.rot90(img)
#     #mask = np.triu(np.ones((w, h)), dtype=int)
#     mask = np.tri(w, h, dtype=int)
    
#     if flipped == 0:
#         fmask = np.expand_dims(mask, 2)
#     if flipped == 1:
#         fmask = np.stack([mask.T, mask, mask], axis=2)
#     if flipped == 2:
#         fmask = np.stack([mask, mask.T, mask], axis=2)
#     if flipped == 3:
#         fmask = np.stack([mask, mask, mask.T], axis=2)
#     if flipped == 4:
#         fmask = np.stack([mask.T, mask.T, mask], axis=2)
#     if flipped == 5:
#         fmask = np.stack([mask.T, mask, mask.T], axis=2)
#     if flipped == 6:
#         fmask = np.stack([mask, mask.T, mask.T], axis=2)
#     if flipped == 7:
#         fmask = fmask = np.expand_dims(mask.T, 2)

#     comp = np.where(fmask, img, img_t)
#     kaleidoscope[0:w, 0:h, :] = comp
#     kaleidoscope[w:, 0:h, :] = np.flip(comp, 1)
#     kaleidoscope[0:w, h:, :] = np.flip(comp, 0)
#     kaleidoscope[w:, h:, :] = np.flip(np.flip(comp, 1), 0)

#     return kaleidoscope

class Kaleidoscope():
    def __init__(self, flipped, size):
        self._flipped = flipped
        self._size = size
        self.mask = None
        self.fmask = None
        self.fmask = self.set_mask(flipped)

    @property
    def size(self):
        return(self._size)

    @size.setter
    def size(self, size):
        self._size = size
        self.fmask = self.set_mask(self.flipped)

    @property
    def flipped(self):
        return(self._flipped)

    @flipped.setter
    def flipped(self, flipped):
        self._flipped = flipped
        self.fmask = self.set_mask(flipped)

    def set_mask(self, flipped):
        mask = np.tri(self.size, self.size, dtype=int)
        if flipped == 0:
            fmask = np.expand_dims(mask, 2)
        elif flipped == 1:
            fmask = np.stack([mask.T, mask, mask], axis=2)
        elif flipped == 2:
            fmask = np.stack([mask, mask.T, mask], axis=2)
        elif flipped == 3:
            fmask = np.stack([mask, mask, mask.T], axis=2)
        elif flipped == 4:
            fmask = np.stack([mask.T, mask.T, mask], axis=2)
        elif flipped == 5:
            fmask = np.stack([mask.T, mask, mask.T], axis=2)
        elif flipped == 6:
            fmask = np.stack([mask, mask.T, mask.T], axis=2)
        elif flipped == 7:
            fmask = np.expand_dims(mask.T, 2)
        return fmask

    def kaleidobase(self, img, fmask):
        #assert img.shape == (self.size, self.size, 3)
        img_t = np.rot90(img)
        comp = np.where(fmask, img, img_t)
        top = np.hstack((comp, comp[:, ::-1, :]))
        kaleidoscope = np.vstack((top, top[::-1, :, :]))
        return kaleidoscope


class Recurseoscope(Kaleidoscope):
    def __init__(self, flipped, size, n_segments):
        super(Recurseoscope, self).__init__(flipped, size)
        self.n_segments = n_segments
        self.size = size / 2
        
        print(self.fmask.shape)

    def kaleide(self, img):
        #assert img.shape == (self.size, self.size, 3)
        for _ in range(self.n_segments):
            img = img[::2, ::2, :]
            img = self.kaleidobase(img, self.fmask)
        return img


class Multiscope(Kaleidoscope):

    def __init__(self, flipped, size, n_segments, alternate_flip=2):
        self.full_size = size
        super(Multiscope, self).__init__(flipped, size)
        self._alternate_flip = None
        self.alternate_flip = alternate_flip
        #self.fmask2 = self.set_mask(alternate_flip)
        self.quick = False
        
        self.segments = None
        self._n_segments = None
        self.seg_size = None
        self.n_segments = n_segments


    @property
    def size(self):
        return(self._size)

    @size.setter
    def size(self, size):
        self._size = size
        #self.n_segments = self.n_segments
        
        self.fmask = self.set_mask(self.flipped)
        self.fmask2 = self.set_mask(self.alternate_flip)

    @property
    def n_segments(self):
        return(self._n_segments)

    @n_segments.setter
    def n_segments(self, n_segments):
        self._n_segments = n_segments
        self.seg_size = int(self.full_size / self.n_segments)
        self.set_segments()
        #if self.n_segments == 0:
            
        self.size = self.seg_size / 2
        if self.seg_size % 2 != 0:
            self.quick = True
            self.size = self.seg_size / 4


    @property
    def alternate_flip(self):
        return(self._alternate_flip)

    @alternate_flip.setter
    def alternate_flip(self, alternate_flip):
        self._alternate_flip = alternate_flip
        self.fmask2 = self.set_mask(alternate_flip)

    def set_segments(self):
        self.segments = np.arange(self.n_segments + 1, dtype=int) * self.seg_size


    def kaleide(self, img):
        if self.n_segments == 0:
            return img
        cnt = 0
        for i in range(1, self.n_segments + 1):
            for j in range(1, self.n_segments + 1):
                if cnt % 2 == 0:
                    thisflip = self.fmask
                else:
                    thisflip = self.fmask2
                if self.quick:
                    img[self.segments[i - 1]:self.segments[i],
                        self.segments[j - 1]:self.segments[j], :] = \
                            self.kaleidobase(img[self.segments[i - 1]:self.segments[i],
                                                 self.segments[j - 1]:self.segments[j], :],
                                             fmask=thisflip)[::2, ::2, :]
                else:
                    img[self.segments[i - 1]:self.segments[i],
                        self.segments[j - 1]:self.segments[j], :] = \
                            self.kaleidobase(img[self.segments[i - 1]:self.segments[i]:2,
                                                 self.segments[j - 1]:self.segments[j]:2, :],
                                             fmask=thisflip)
                cnt += 1
        return img


# make one knob me the number of channels that are flipped
# make a different knob be how much of the image is being kaleidoscoped
# make another knob be wether its one flipped one normal or all flipped and mirrored






