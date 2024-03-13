import uuid
import numpy as np
import values
from pydub import AudioSegment
from scipy.signal import spectrogram
from scipy.ndimage import maximum_filter

# NOTE: 
# Helper function that performs a spectrogram with the values in values.
# Adding the sample rate and FFT_WINDOW_SIZE
def my_spectrogram(audio):
    nperseg = int(values.SAMPLE_RATE * values.FFT_WINDOW_SIZE)
    return spectrogram(audio, values.SAMPLE_RATE, nperseg=nperseg)


def file_to_spectrogram(filename):
    a = AudioSegment.from_file(filename).set_channels(1).set_frame_rate(values.SAMPLE_RATE)
    audio = np.frombuffer(a.raw_data, np.int16)
    # NOTE:
    # audio contains the overall amplitute at an instant of time
    return my_spectrogram(audio)

# NOTE: 
# takes Sxx and samples the peaks and selects the largest peaks
def find_peaks(Sxx):

    data_max = maximum_filter(Sxx, size=values.PEAK_BOX_SIZE, mode='constant', cval=0.0)
    peak_goodmask = (Sxx == data_max)  # good pixels are True
    y_peaks, x_peaks = peak_goodmask.nonzero()
    # print(y_peaks)
    # print(x_peaks)
    peak_values = Sxx[y_peaks, x_peaks]
    i = peak_values.argsort()[::-1]
    # print(i)
    # # get co-ordinates into arr
    j = [(y_peaks[idx], x_peaks[idx]) for idx in i]
    total = Sxx.shape[0] * Sxx.shape[1]
    # in a square with a perfectly spaced grid, we could fit area / PEAK_BOX_SIZE^2 points
    # use point efficiency to reduce this, since it won't be perfectly spaced
    # accuracy vs speed tradeoff
    peak_target = int((total / (values.PEAK_BOX_SIZE**2)) * values.POINT_EFFICIENCY)
    return j[:peak_target]

# NOTE: takes in pairs of idicies of Sxx and gives a list of pairs of f, t
def idxs_to_tf_pairs(idxs, t, f):
    return np.array([(f[i[0]], t[i[1]]) for i in idxs])




# NOTE: Generate hashes for a song produces a list of hashes
def fingerprint_file(filename):
    f, t, Sxx = file_to_spectrogram(filename)
    # NOTE:
    # f -> contains all the freqencies
    # t -> all the time stamps
    # Sxx is a 2D array containg info like Sxx[i][j] is the amplitude of frequency f[i] and at time t[j]

    peaks = find_peaks(Sxx)
    # NOTE: 
    # peaks contains a list of tuples containing i,j indices of Sxx 
    peaks = idxs_to_tf_pairs(peaks, t, f)
    # NOTE: 
    # peaks now contains a list of tuples containing f,t pairs of all the important peaks
    return hash_points(peaks, filename)

# NOTE:
# computes the hashes of each point in peaks then returns a list of (hash, start_time, song_id)
def hash_points(points, filename):
    hashes = []
    song_id = uuid.uuid5(uuid.NAMESPACE_OID, filename).int
    for anchor in points:
        for target in target_zone(
            anchor, points, values.TARGET_T, values.TARGET_F, values.TARGET_START
        ):
            hashes.append((
                # hash
                hash_point_pair(anchor, target),
                # start_time
                anchor[1],
                # filename
                str(song_id)
            ))
    return hashes

# NOTE:
# computes hash of f1, f2, t2 - t1
def hash_point_pair(p1, p2):
    return hash((p1[0], p2[0], p2[1]-p1[1]))


# NOTE:
# takes in width, height, seperation and yeilds points in that target zone
def target_zone(anchor, points, width, height, sepration):
    x_min = anchor[1] + sepration
    x_max = x_min + width
    y_min = anchor[0] - (height*0.5)
    y_max = y_min + height
    for point in points:
        if point[0] < y_min or point[0] > y_max:
            continue
        if point[1] < x_min or point[1] > x_max:
            continue
        yield point

