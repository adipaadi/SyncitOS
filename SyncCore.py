import sounddevice as sd
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt

samplerate = 44100
channels = 1
duration = 10

peak_times = []


def calculate_bpm(peak_times):
    if len(peak_times) < 2:
        return 0
    intervals = np.diff(peak_times)
    avg_interval = np.mean(intervals)
    bpm = 60 / avg_interval
    return bpm


def butter_bandpass(lowcut, highcut, samplerate, order=4):
    nyquist = 0.5 * samplerate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band', analog=False)
    return b, a


def apply_filter(indata, b, a):
    return filtfilt(b, a, indata, axis=0)

#frequencies
lowcut_kick = 20.0
highcut_kick = 60.0
b_kick, a_kick = butter_bandpass(lowcut_kick, highcut_kick, samplerate)


def audio_callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")

    normalized_data = indata / np.max(np.abs(indata))

    filtered_data_kick = apply_filter(normalized_data[:, 0], b_kick, a_kick)

    peaks_kick, _ = find_peaks(filtered_data_kick, height=0.05) 

    if len(peaks_kick) > 0:
        peak_times.extend(peaks_kick / samplerate)  

        bpm = calculate_bpm(peak_times)


print("Recording...")

with sd.InputStream(samplerate=samplerate, channels=channels, callback=audio_callback, dtype='float32'):
    sd.sleep(duration * 10000)

print("Recording finished.")
