import numpy as np

class Kaleidoscope():
    def __init__(self, flipped, size):
        self._flipped = flipped
        self._size = size
        self.mask = None
        self.fmask = None
        self.fmask = self.get_mask(flipped)

    @property
    def size(self):
        return(self._size)

    @size.setter
    def size(self, size):
        if self._size != size:
            self._size = size
            self.fmask = self.get_mask(self.flipped)

    @property
    def flipped(self):
        return(self._flipped)

    @flipped.setter
    def flipped(self, flipped):
        if self._flipped != flipped:
            self._flipped = flipped
            self.fmask = self.get_mask(flipped)

    def get_mask(self, flipped, mask=None):
        if mask is None:
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
        self._size = size / 2

    @property
    def size(self):
        return(self._size)

    @size.setter
    def size(self, size):
        if (size / 2) != self._size:
            self._size = size / 2
            self.fmask = self.get_mask(self.flipped)

    def kaleide(self, img):
        #print(self.size)
        #assert img.shape == (self.size, self.size, 3)
        for _ in range(self.n_segments):
            img = img[::2, ::2, :]
            img = self.kaleidobase(img, self.fmask)
        return img


class Multiscope(Kaleidoscope):

    def __init__(self, flipped, size, n_segments, alternate_flip=2):
        self._full_size = size # full size is the size of the canvas
        super(Multiscope, self).__init__(flipped, size)
        self._alternate_flip = None
        self.alternate_flip = alternate_flip
        #self.fmask2 = self.get_mask(alternate_flip)
        self.quick = True
        self.segments = None
        self._n_segments = None
        self.seg_size = None # seg_size is the size of each segment
        self.n_segments = n_segments


    @property
    def size(self):
        # size is is the size of the mask (could be half the segment size for
        # efficiency)
        return(self._size)

    @size.setter
    def size(self, size):
        if self._size != size:
            self._size = size
            self.fmask = self.get_mask(self.flipped)
            self.fmask2 = self.get_mask(self.alternate_flip)


    @property
    def full_size(self):
        return(self._full_size)

    @full_size.setter
    def full_size(self, full_size):
        if self._full_size != full_size:
            self._full_size = full_size
            self.set_segments()

    @property
    def n_segments(self):
        return(self._n_segments)

    @n_segments.setter
    def n_segments(self, n_segments):
        if self._n_segments != n_segments:
            self._n_segments = n_segments
            self.set_segments()

                


    def set_segments(self):
        if self.n_segments == 0:
            pass
        else:
            self.seg_size = int(self.full_size / self.n_segments)
            segm = self.get_segments()

            if self.seg_size % 2 == 0:
                quick = True
                size = self.seg_size / 2
            else:
                quick = False
                size = self.seg_size

            self.quick = quick
            self.segments = segm
            self.size = size

    @property
    def alternate_flip(self):
        return(self._alternate_flip)

    @alternate_flip.setter
    def alternate_flip(self, alternate_flip):
        if self._alternate_flip != alternate_flip:
            self._alternate_flip = alternate_flip
            self.fmask2 = self.get_mask(alternate_flip)

    def get_segments(self):
        return np.arange(self.n_segments + 1, dtype=int) * self.seg_size


    def kaleide(self, img):
        #print(segm, self.quick, self.seg_size, self.size, self.full_size, self.n_segments)
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
                    img[(self.segments)[i - 1]:(self.segments)[i],
                        (self.segments)[j - 1]:(self.segments)[j], :] = \
                        self.kaleidobase(
                            img[(self.segments)[i - 1]:(self.segments)[i]:2,
                                (self.segments)[j - 1]:(self.segments)[j]:2, :],
                            fmask=thisflip)
                else:
                    img[(self.segments)[i - 1]:(self.segments)[i],
                        (self.segments)[j - 1]:(self.segments)[j], :] = \
                        self.kaleidobase(
                            img[(self.segments)[i - 1]:(self.segments)[i],
                                (self.segments)[j - 1]:(self.segments)[j], :],
                            fmask=thisflip)[::2, ::2, :]
                cnt += 1
        return img


# make one knob me the number of channels that are flipped
# make a different knob be how much of the image is being kaleidoscoped
# make another knob be wether its one flipped one normal or all flipped and mirrored



class KaleidoscopeMultiMirror():

    def __init__(self, flipped, size):
        self._flipped = flipped
        self._size = size

        self._rotations = [120, 240, 360]
        self._rotations_dir = [True, True, True]
        self.masks = []
        self.pixel_mappings = []

    @property
    def size(self):
        return(self._size)

    @size.setter
    def size(self, size):
        self._size = size
        self.reinit_kaleidoscope()


    @property
    def rotations(self):
        return(self._rotations)

    @rotations.setter
    def rotations(self, rotations):
        self._rotations = rotations
        self.reinit_kaleidoscope()

    @property
    def rotations_dir(self):
        return(self._rotations_dir)

    @rotations_dir.setter
    def rotations_dir(self, rotations_dir):
        self._rotations_dir = rotations_dir
        self.reinit_kaleidoscope()


    @property
    def flipped(self):
        return(self._flipped)

    @flipped.setter
    def flipped(self, flipped):
        self._flipped = flipped
        self.reinit_kaleidoscope()

    def reinit_kaleidoscope(self):
        ii, jj = abs(np.mgrid[0:self.size, 0:self.size])
        self.masks = []
        self.pixel_mappings = []
        #if len(self.rotations) == 0:
         #   self.pixel_mappings.append((new_ix_i, new_ix_j))
        
        for i, r in enumerate(self.rotations):
            a, b = get_params(r, int(self.size / 2), int(self.size / 2))
            d = get_dist_to_line(a, b, ii, jj)
            puv = get_perp_uv(a)
            i_mv_px_by, j_mv_px_by = get_reflection_delta(d, puv)
            # TODO: clip??
            # new_ix_i = np.clip(ii - i_mv_px_by - 1, -self.size, self.size - 1)
            # new_ix_j = np.clip(jj - j_mv_px_by - 1, -self.size, self.size - 1)
            new_ix_i = np.clip(ii - i_mv_px_by - 1, 0, self.size - 1)
            new_ix_j = np.clip(jj - j_mv_px_by - 1, 0, self.size - 1)

            self.pixel_mappings.append((new_ix_i, new_ix_j))

            cond = ii < (a * jj + b)
            cond = self.get_mask(self.flipped, cond)
            self.masks.append(cond)


    def get_mask(self, flipped, mask):
        if flipped == 0:
            fmask = np.expand_dims(mask, 2)
        elif flipped == 1:
            fmask = np.stack([~mask, mask, mask], axis=2)
        elif flipped == 2:
            fmask = np.stack([mask, ~mask, mask], axis=2)
        elif flipped == 3:
            fmask = np.stack([mask, mask, ~mask], axis=2)
        elif flipped == 4:
            fmask = np.stack([~mask, ~mask, mask], axis=2)
        elif flipped == 5:
            fmask = np.stack([~mask, mask, ~mask], axis=2)
        elif flipped == 6:
            fmask = np.stack([mask, ~mask, ~mask], axis=2)
        elif flipped == 7:
            fmask = np.expand_dims(~mask, 2)
        return fmask


    def kaleide(self, pic):
        for i, r in enumerate(self.rotations):
            mask = self.masks[i]
            px_map_i, px_map_j = self.pixel_mappings[i]
            refl = pic[px_map_i, px_map_j, :]
            if self._rotations_dir[i]:
                pic = np.where(mask, pic, refl)
            else:
                pic = np.where(~mask, pic, refl)

        # right_half = pic[:, int(self.size / 2):, :]
        # pic[:, :int(self.size / 2), :] = np.flip(right_half, axis=1)
        return pic





def get_params(alpha, ptx, pty):
    """Find  the linear equation parameters for a line of angle alpha that
    passes through ptx and pty.

    Parameters
    ----------
    alpha : float
        angle
    ptx : int
        x value
    pty : int
        y value

    Returns
    -------
    a, b
        parameters a and b from ax+b
    """
    a = np.tan(np.deg2rad(alpha))
    # y = a*x + b
    # y-b = a*x
    # -b = a*x -y
    # b = -a*x +y
    b = -ptx * a + pty
    return a, b


def get_dist_to_line(pa, pb, i, j):
    """given the line defined by `pa*x+pb`, gets the distance of each point in
    i, j.

    Parameters
    ----------
    pa : float
        rise parameter
    pb : float
        intercept parameter
    i : array
        i indexes
    j : array
        j indexes

    Returns
    -------
    array
        array where each point is the distance of the point (i, j) to the line
    """
    p = np.stack((j, i), axis=2)
    a = np.array([0, pb])
    b = np.array([1, pa])
    top = np.cross((p-a), b, axisa=2, axisb=0)
    bottom = np.linalg.norm(b)
    return top/bottom

def get_perp_uv(a):
    """
    finds the unit vector that is perpendicular to a line with rise parameter a
    """
    uv = np.array([1,a])
    uv_len = np.sqrt(np.sum(uv**2))
    uv = uv/uv_len
    puv = np.array([a, -1])
    puv_len = np.sqrt(np.sum(puv**2))
    puv = puv/puv_len
    return puv

def get_reflection_delta(other, puv):
    """
    given the distance to the line and the perpendicular unit vector, gets the
    amount of pixels that each point needs to move by
    """
    i_mv_px_by = (other * (puv[1]) * 2).astype(int)
    j_mv_px_by = (other * (puv[0]) * 2).astype(int)
    return i_mv_px_by, j_mv_px_by