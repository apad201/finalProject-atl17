import numpy as np
import math
from matplotlib import pyplot as plt
from scipy.io.wavfile import read, write
import scipy.fft as fourier

def makeMono(signal):
	return np.int16((signal[:,0] + signal[:,1])/2)

def fourierTransform(signal, sampleRate):
	length = len(signal)
	freqs = fourier.rfftfreq(length, 1/sampleRate)
	amplitudes = fourier.rfft(signal)
	return freqs, amplitudes

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

def trimFreqs(freqs, amps):
	p = freqs.argsort()
	

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
	rate, signal = read("audioSample.wav")
	monoSignal = np.int16((signal[:,0] + signal[:,1])/2)
	write("monoAudioSample.wav", rate, monoSignal) 
	# checking that making signal mono works as intended without ruining audio
	
	freqs, amps = fourierTransform(monoSignal, rate)
	plotFreqs(freqs, np.abs(amps), "Frequency domain plot", "Frequency", "Amplitude", "sampleFreqPlot")
	plotFreqs(freqs, np.abs(amps), "Frequency domain plot", "Frequency", "Amplitude", "sampleFreqPlotTrimmed", removeHigh = True)