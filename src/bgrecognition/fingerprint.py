import uuid
import numpy as np
import values
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter

def my_spectrogram(audio):
    """Helper function that performs a spectrogram with the values in values."""
    nperseg = int(values.SAMPLE_RATE * values.FFT_WINDOW_SIZE)
    return spectrogram(audio, values.SAMPLE_RATE, nperseg=nperseg)


def file_to_spectrogram(filename):
    """Calculates the spectrogram of a file.

    Converts a file to mono and resamples to :data:`~abracadabra.values.SAMPLE_RATE` before
    calculating. Uses :data:`~abracadabra.values.FFT_WINDOW_SIZE` for the window size.

    :param filename: Path to the file to spectrogram.
    :returns: * f - list of frequencies
              * t - list of times
              * Sxx - Power value for each time/frequency pair
    """
    a = AudioSegment.from_file(filename).set_channels(1).set_frame_rate(values.SAMPLE_RATE)
    audio = np.frombuffer(a.raw_data, np.int16)
    return my_spectrogram(audio)

def find_peaks(Sxx):
    """Finds peaks in a spectrogram.

    Uses :data:`~abracadabra.values.PEAK_BOX_SIZE` as the size of the region around each
    peak. Calculates number of peaks to return based on how many peaks could theoretically
    fit in the spectrogram and the :data:`~abracadabra.values.POINT_EFFICIENCY`.

    Inspired by
    `photutils
    <https://photutils.readthedocs.io/en/stable/_modules/photutils/detection/core.html#find_peaks>`_.

    :param Sxx: The spectrogram.
    :returns: A list of peaks in the spectrogram.
    """
    data_max = maximum_filter(Sxx, size=values.PEAK_BOX_SIZE, mode='constant', cval=0.0)
    peak_goodmask = (Sxx == data_max)  # good pixels are True
    y_peaks, x_peaks = peak_goodmask.nonzero()
    print(y_peaks)
    print(x_peaks)
    peak_values = Sxx[y_peaks, x_peaks]
    i = peak_values.argsort()[::-1]
    print(i)
    # # get co-ordinates into arr
    j = [(y_peaks[idx], x_peaks[idx]) for idx in i]
    total = Sxx.shape[0] * Sxx.shape[1]
    # in a square with a perfectly spaced grid, we could fit area / PEAK_BOX_SIZE^2 points
    # use point efficiency to reduce this, since it won't be perfectly spaced
    # accuracy vs speed tradeoff
    peak_target = int((total / (values.PEAK_BOX_SIZE**2)) * values.POINT_EFFICIENCY)
    return j[:peak_target]


def idxs_to_tf_pairs(idxs, t, f):
    """Helper function to convert time/frequency indices into values."""
    return np.array([(f[i[0]], t[i[1]]) for i in idxs])

def fingerprint_file(filename):
    """Generate hashes for a file.

    Given a file, runs it through the fingerprint process to produce a list of hashes from it.

    :param filename: The path to the file.
    :returns: The output of :func:`hash_points`.
    """
    f, t, Sxx = file_to_spectrogram(filename)
    peaks = find_peaks(Sxx)
    peaks = idxs_to_tf_pairs(peaks, t, f)
    return hash_points(peaks, filename)

def hash_points(points, filename):
    """Generates all hashes for a list of peaks.

    Iterates through the peaks, generating a hash for each peak within that peak's target zone.

    :param points: The list of peaks.
    :param filename: The filename of the song, used for generating song_id.
    :returns: A list of tuples of the form (hash, time offset, song_id).
    """
    hashes = []
    song_id = uuid.uuid5(uuid.NAMESPACE_OID, filename).int
    for anchor in points:
        for target in target_zone(
            anchor, points, values.TARGET_T, values.TARGET_F, values.TARGET_START
        ):
            hashes.append((
                # hash
                hash_point_pair(anchor, target),
                # time offset
                anchor[1],
                # filename
                str(song_id)
            ))
    return hashes

def hash_point_pair(p1, p2):
    """Helper function to generate a hash from two time/frequency points."""
    return hash((p1[0], p2[0], p2[1]-p1[1]))

def target_zone(anchor, points, width, height, t):
    """Generates a target zone as described in `the Shazam paper
    <https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf>`_.

    Given an anchor point, yields all points within a box that starts `t` seconds after the point,
    and has width `width` and height `height`.

    :param anchor: The anchor point
    :param points: The list of points to search
    :param width: The width of the target zone
    :param height: The height of the target zone
    :param t: How many seconds after the anchor point the target zone should start
    :returns: Yields all points within the target zone.
    """
    x_min = anchor[1] + t
    x_max = x_min + width
    y_min = anchor[0] - (height*0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point




if __name__ == "__main__":
    path="C:\\Users\\DELL\\Desktop\\shazam\\[01 - Urike Urike.mp3"
    f, t, Sxx = file_to_spectrogram(path)
    print("Frequencies:", f)
    print("Times:", t)
    print("Spectrogram:", Sxx)
    hashes=fingerprint_file(path)
    for hash_value, time_offset, song_id in hashes:
         print("Hash:", hash_value)
         print("Time Offset:", time_offset)
         print("Song ID:", song_id)
