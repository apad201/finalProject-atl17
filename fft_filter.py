import numpy as np
import math
from matplotlib import pyplot as plt
from scipy.io.wavfile import read, write
from scipy.special import expit
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
	xMax (optional): upper limit for x-axis, if not included, will show all
					 x-values passed	 
	
OUTPUTS: none
"""
def plotFreqs(x, y, title, xLab, yLab, fileName, xMax = None):
	plt.figure()
	fig, ax = plt.subplots()
	ax.plot(x, y)
	plt.title(title)
	plt.xlabel(xLab)
	plt.ylabel(yLab)
	if xMax is not None:
		plt.xlim([0,xMax])
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

"""
LP: a sigmoid-based frequency-domain low-pass filter

INPUTS:
	freqs: np.array containing centers of frequency bins from rfftfreq
	powers: np.array containing rfft of signal
	centerFreq: frequency at which sigmoid should reach 0.5
	ramp: steepness of sigmoid (i.e. coefficient of x values in sigmoid fn.
		  recommended around 0.05-0.1)
		  
OUTPUTS:
	powersHP: powers scaled by appropriate HP frequency response curve
"""
def LP(freqs, powers, centerFreq, ramp):
	LPfilter = expit(ramp * (centerFreq - freqs))
	return powers * LPfilter

"""
HP: a sigmoid-based frequency-domain high-pass filter

same as calling LP(-1 * freqs, powers, -centerFreq, ramp)
or calling LP(freqs, powers, centerFreq, -ramp)
"""
def HP(freqs, powers, centerFreq, ramp):
	HPfilter = expit(ramp * (freqs - centerFreq))
	return powers * HPfilter

"""
BP: a sigmoid-based frequency-domain band-pass filter

INPUTS:
	freqs: np.array containing centers of frequency bins from rfftfreq
	powers: np.array containing rfft of signal
	lowerFreq, upperFreq: floats/ints containing lower and upper bounds of band
	ramp: steepness of sigmoid on both sides (recommended 0.05-0.1)

OUTPUTS:
	powersBP: powers scaled by appropriate BP frequency response curve
"""
def BP(freqs, powers, lowerFreq, upperFreq, ramp):
	BPfilter = expit(ramp * (lowerFreq - freqs)) + expit(ramp * (freqs - upperFreq)) - 1
	return powers * BPfilter


if __name__ == "__main__":
	# Read in sample audio signal:
	rate, signal = read("audioSample.wav")
	
	# make mono:
	monoSignal = makeMono(signal)
	
	# checking that making signal mono works as intended without ruining audio:
	# write("monoAudioSample.wav", rate, monoSignal) 
	
	# Apply FFT:
	freqs, powers = fourierTransform(monoSignal, rate)
	
	plotFreqs(freqs, np.abs(powers), "Frequency domain plot", "Frequency",\
			  "Power", "sampleFreqPlot")
	plotFreqs(freqs, np.abs(powers), "Frequency domain plot", "Frequency",\
			  "Power", "sampleFreqPlotTrimmed", xMax = 1000)
	
	# Apply naive low-pass filter:
	powersLP = naiveLP(freqs, powers, 440)
	plotFreqs(freqs, np.abs(powersLP), "Naive LP filter frequency plot",\
			  "Frequency", "Power", "sampleNaiveLP", xMax = 1000)
	LPsignal = inverseFourierTransform(powersLP)
	write("LPsignal1.wav", rate, LPsignal)
	
	# Now try applying less-naive LP filter:
	powersLP2 = LP(freqs, powers, 440, 0.075)
	plotFreqs(freqs, np.abs(powersLP2), "LP filter frequency plot", \
							"Frequency", "Power", "sampleSigmoidLP",
							xMax = 1000)
	LPsignal2 = inverseFourierTransform(powersLP2)
	write("LPsignal2.wav", rate, LPsignal2)
	
	# Apply high-pass filter:
	powersHP = HP(freqs, powers, 440, 0.075)
	plotFreqs(freqs, np.abs(powersHP), "HP filter frequency plot", \
			  "Frequency", "Power", "sampleSigmoidHP", xMax = 1000)
	HPsignal = inverseFourierTransform(powersHP)
	write("HPsignal.wav", rate, HPsignal)
	
	# Apply band-pass filter:
	powersBP = BP(freqs, powers, 440, 880, 0.075)
	plotFreqs(freqs, np.abs(powersBP), "BP filter frequency plot", \
			  "Frequency", "Power", "sampleSigmoidBP", xMax = 1000)
	BPsignal = inverseFourierTransform(powersBP)
	write("BPsignal.wav", rate, BPsignal)
	
	# Test frequency separation on another file:
	
	rate, signal = read("audioSample2.wav")
	monoSignal = makeMono(signal)
	
	freqs, powers = fourierTransform(monoSignal, rate)
	plotFreqs(freqs, np.abs(powers), "Frequency domain plot", "Frequency",\
			  "Power", "sampleFreqPlot2", xMax = 4000)
	
	# Filter out everything above middle C (should filter out all strings)
	powersLP = LP(freqs, powers, 262, 0.075)
	plotFreqs(freqs, np.abs(powersLP), "LP filter frequency plot", "Frequency",\
			  "Power", "sampleSigmoidLP2", xMax = 4000)
	LPsignal = inverseFourierTransform(powersLP)
	write("separatedSignal.wav", rate, LPsignal)
	
		