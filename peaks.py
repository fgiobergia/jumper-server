import numpy as np
from scipy.signal import find_peaks


def pks(x):
    # max freq: 3 Hz. Sampling @ 25 Hz: 1 peak each 8 samples --> distance=8
    distance = 25//3

    prominence = 1000
    p = find_peaks(x, distance=distance, prominence=prominence)[0]
    # d is the distance between the i-th peak and
    # the (i+1)-th. We do not have distance for the
    # final peak (see below how we handle this)
    d = p[1:] - p[:-1]

    # jump frequency: ~1.5 - 3 Hz.
    # @25 Hz sampling, we should expect
    # between 8 and 15 samples between
    # jumps. Peaks outside of this range
    # are discarded
    m1 = (d>=8)&(d<=15)

    if m1.shape == (0,):
        return []

    # the approach makes it so that we do not know
    # the outcome for the final peak (it does not have
    # a subsequent peak to compare it to). The adopted
    # policy is that if the last but one is a peak, then
    # also the last one is considered a peak
    m2 = np.append(m1, m1[-1])
    return p[m2]

def find_skips(readings):

    xyz = [ v[1] for v in sorted(readings.items(), key=lambda x: x[0]) ]
    x = [ x for x,_,_ in xyz ]
    y = [ y for _,y,_ in xyz ]
    z = [ z for _,_,z in xyz ]

    peaks_x = pks(x)
    peaks_y = pks(y)
    peaks_z = pks(z)

    return int(round(np.mean([len(peaks_x), len(peaks_y), len(peaks_z)])))

