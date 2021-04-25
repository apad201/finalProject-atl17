import numpy as np
import math
from matplotlib import pyplot as plt
from scipy.io.wavfile import read, write
import scipy.fft as fourier

"""
makeMono: makes a stereo audio signal into a mono signal

INPUTS: signal (2-dimensional np.array)

OUTPUTS: monoSignal (1-dimensional np.array, with each entry being the average
		of the two corresponding entries in signal)
"""
def makeMono(signal):
	return np.int16((signal[:,0] + signal[:,1])/2)

"""
fourierTransform: uses scipy's rfft to take DFT of signal 

INPUTS: signal (1-dimensional np.array), sampleRate (sample rate of signal)

OUTPUTS: freqs (list of centers of frequency bins for DFT), powers (fourier 
transform of signal, in a complex np.array)
"""
def fourierTransform(signal, sampleRate):
	length = len(signal)
	freqs = fourier.rfftfreq(length, 1/sampleRate)
	powers = fourier.rfft(signal)
	return freqs, powers

"""
inverseFourierTransform: takes inverse FFT of given np.array and normalizes
result for storing in 16-bit WAV file

INPUTS: powers (complex np.array containing possibly modified output of rfft)

OUTPUTS: signal (normalized 16-bit int np.array containing audio signal; 
		sample rate needs to be tracked in order to write to audio file)
"""
def inverseFourierTransform(powers):
	signal = fourier.irfft(powers)
	signal = np.int16(signal * (32767 / signal.max()))
	return signal

"""
plotFreqs: creates frequency domain plot

INPUTS: 
	x: x-axis variable, usually freqs
	y: y-axis variable, usually np.abs(powers)
	title: plot title (string)
	xLab, yLab: x- and y-axis labels (strings)
	fileName: filename (string)
	removeHigh: bool, if True, will only show frequencies from 0-5000 Hz. 
	
OUTPUTS: none
"""
def plotFreqs(x, y, title, xLab, yLab, fileName, removeHigh = False):
	plt.figure()
	fig, ax = plt.subplots()
	ax.plot(x, y)
	plt.title(title)
	plt.xlabel(xLab)
	plt.ylabel(yLab)
	if removeHigh:
		plt.xlim([0,5000])
	plt.savefig(fileName+'.png', bbox_inches='tight')
	plt.close('all')
	return

"""
naiveLP: a naive frequency-domain low-pass filter

INPUTS: freqs (np.array containing centers of frequency bins), powers (complex
np.array containing output of rfft), cutoff (frequency cutoff)

OUTPUTS: filteredPowers (powers np.array with all entries corresponding to
frequency bins with center above cutoff frequency set to 0)
"""
def naiveLP(freqs, powers, cutoff):
	filteredPowers = powers.copy()
	for i in range(len(freqs)):
		if freqs[i] > cutoff:
			filteredPowers[i] = 0.0 + 0.0j
	return filteredPowers
	
def LP(freqs, powers, centerFreq, ramp):
	LPfilter = 1/(1 + np.exp(ramp*(freqs - centerFreq)))
	return powers * LPfilter

if __name__ == "__main__":
	
	"""
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
	"""
	
	# Read in sample audio signal
	rate, signal = read("audioSample.wav")
	
	# make mono
	monoSignal = np.int16((signal[:,0] + signal[:,1])/2)
	# write("monoAudioSample.wav", rate, monoSignal) 
	# checking that making signal mono works as intended without ruining audio
	
	# Apply FFT
	freqs, powers = fourierTransform(monoSignal, rate)
	
	"""
	plotFreqs(freqs, np.abs(powers), "Frequency domain plot", "Frequency", "Power", "sampleFreqPlot")
	plotFreqs(freqs, np.abs(powers), "Frequency domain plot", "Frequency", "Power", "sampleFreqPlotTrimmed", removeHigh = True)
	
	# Apply naive low-pass filter
	powersLP = naiveLP(freqs, powers, 440)
	# plotFreqs(freqs, np.abs(powersLP), "Filtered frequency plot", "Frequency", "Power", "sampleFreqPlotFiltered", removeHigh = True)
	
	# Transform back into signal and save
	filteredSignal = inverseFourierTransform(powersLP)
	write("testingTransformedSignal.wav", rate, filteredSignal)
	"""
	# Now try applying less-naive LP filter
	powersLP2 = LP(freqs, powers, 440, 0.075)
	
	# Tranform back into signal and save
	filteredSignal2 = inverseFourierTransform(powersLP2)
	write("testingTransformedSignal2.wav", rate, filteredSignal2)