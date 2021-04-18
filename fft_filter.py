import numpy as np
import math
from matplotlib import pyplot as plt
from scipy.io.wavfile import write
import scipy.fft as fourier

srate = 44100
length = 5

x = np.linspace(0, length, srate*length, endpoint=False)
y = np.sin(2 * np.pi * 440 * x) + np.sin(2 * np.pi * 277.18 * x)

normY = np.int16(y / y.max() * 32767)

write("testingWavFile.wav", srate, normY) # should sound like a minor 6 with
										  # C#4 and A4

freqs = fourier.rfftfreq(srate * length, 1 / srate)
amplitudes = fourier.rfft(normY)

plt.plot(freqs, np.abs(amplitudes))
plt.show()
