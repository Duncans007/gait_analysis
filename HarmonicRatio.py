# This class is part of a set of gait analysis tools.
# This class is designed to process data as described in the cited excerpt below, retrieving a "hr" (harmonic ratio).
# This class has been further modified to determine hr over time of a given signal.
# This class will be updated to take constant signal and gait input, and self-determine when to update the hr

# Excerpt:
# The HR was calculated by decomposing acceleration signals into harmonics using a discrete Fourier transform[14];
# the summed amplitudes of the first 10 even harmonics were then divided by the summed amplitudes of the first 10 odd
# harmonics for the AP and V accelerations, and vice-versa for the ML accelerations.
# This difference is due to the fact that whereas the AP and V accelerations have two periods every stride,
# showing a dominance of the second harmonic, representing step frequency and subsequent even harmonics,
# ML accelerations have only one period per stride, reflecting a dominance of the first (and subsequent odd) harmonics [14].
# A higher HR is an indication of increased smoothness of gait, which can be interpreted as increased stability.
# From: Bisi, Maria & Riva, Federico & Stagni, Rita. (2014). Measures of gait stability: Performance on adults and toddlers at the beginning of independent walking. Journal of neuroengineering and rehabilitation. 11. 131. 10.1186/1743-0003-11-131.
# [14] Menz HB, Lord SR, Fitzpatrick RC: Acceleration patterns of the head and pelvis when walking are associated with risk of falling in community-dwelling older people. J Gerontol A Biol Sci Med Sci 2003.

import numpy as np
import plotly.express as px
import pandas as pd
from scipy import fft


class HarmonicRatio:
    # Variables to Initialize
    # dir -> "x"(AP), "y"(V), "z"(ML)
    # freq -> frequency of signal in Hz
    # rw -> read/write permissions, same as used in open(). Defaults to overwriting (w+). Appending is a+


    def __init__(self, dir, freq, rw="w+"):
        #input initializations
        self.rw = rw
        self.axis = dir.lower()
        if self.axis not in ["x", "y", "z"]:
            #Verify that axis is valid and prevent object creation without
            raise Exception("Invalid axis in initialization of HarmonicRatio(), use X/Y/Z.")


        #Other variable initializations
        self.current_period = [] #Constantly refreshed array for most immediate analysis

        self.hr = -1 #initialize return value as -1 so immediate red flag if code is not running.
        self.data_refresh_rate = freq #Hz

        self.last_gait_var = -1 #currently unused
        self.saved_output_vars = []  #currently unused


    def analyze_dataset(self, dataset, window_size, window_delta, filename=""):
        # Function to analyze complete dataset and save plots to html file.
        # Returns array of harmonic ratio values starting at frame window_delta, then incrementing by the same.
        # dataset -> single dimension time values of signal
        # window_size -> length of window for each individual harmonic analysis
        # window_delta -> increment of window after each analysis
        # filename -> .HTML file for charts to output after each run

        hr_arr = []
        # iterate over dataset, processing each window and saving the hr to an array to plot
        for n in range(window_size, len(dataset), window_delta):
            self.current_period = dataset[n - window_size:n]
            hr_arr.append(self.process_event())

        #create array of x values to plot the y values against
        x_arr = np.multiply(list(range(window_size // window_delta, len(hr_arr) + window_size // window_delta)),
                            window_delta)

        #If filename is not filled in, skip file output and just return array of harmonic ratio values
        if filename != "":
            with open(filename, self.rw) as f:
                f.write(f"<h1>Harmonic Ratio of Signal Over Time</h1>\n")
                f.write(f"<h2>Window Size:{window_size}</h2>\n")
                f.write(f"<h2>Window Delta:{window_delta}</h2>\n")
                f.write("<hr>\n<hr>\n")
                f.write(f"<h3>Signal Plot Over Time:</h3>\n")
                self.plot_line(dataset, list(range(0, len(dataset))), f)
                f.write(f"<h3>Harmonic Ratio over Time:</h3>\n")
                self.plot_line(hr_arr, x_arr, f)

        return hr_arr


    def process_event(self):
        # Process current_period array to extract and return harmonic ratio

        N = len(self.current_period) # number of sample points
        T = 1 / self.data_refresh_rate # sample spacing (refresh rate)

        #use fft on signal to obtain frequency domain representation
        fft_output = fft.rfft(self.current_period)
        fft_freqs = fft.rfftfreq(N, T)

        #display functions for individual testing
        #self.plot_line(self.current_period, list(range(0, N)))
        self.plot_line(np.abs(fft_output), fft_freqs)
        #print(fft_freqs)

        #sums first 10 even and odd harmonic amplitudes
        even_harmonics = 0
        odd_harmonics = 0
        for x in range(0, 20):
            if x % 2 == 0:
                #odd
                odd_harmonics += np.abs(fft_output[x])
                #print(f"odd:{odd_harmonics}")
            else:
                #even
                even_harmonics += np.abs(fft_output[x])
                #print(f"even:{even_harmonics}")

        # calculates appropriate ratio based on axis of computation
        try:
            if self.axis == "z":
                hr = odd_harmonics / even_harmonics
            else:
                hr = even_harmonics / odd_harmonics
        except:
            hr = 0

        #print(even_harmonics, odd_harmonics, hr, np.sum(self.current_period))
        return np.real(hr)


    def plot_line(self, y, x, f, title=''):
        ## Generate line plot of a single-dimension signal over time
        # y -> 1d signal values
        # x -> time/frequency values of equal length to y
        # f -> file object for saving
        # title -> plot title

        df = pd.DataFrame(dict(
            x=x,
            y=y
        ))
        fig = px.line(df, x="x", y=df.columns[0:len(y)], title=title)
        #fig.show()
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("<hr>\n<hr>\n")

        return 0


# todo:
#    def insert_pt(self, datapt, gaitVar):
#        # Add a single datapoint to the analyzer and determine if event can be processed
#        # gaitVar input assumes 0 for stance phase and >0 for swing phase
#
#        # Save single point of signal
#        self.current_period.append(datapt)
#
#        # Determine if the relevant gait cycle is complete using gait variable
#        process = False
#        if self.last_gait_var != gaitVar and len(self.current_period) > 5 and self.last_gait_var != -1:
#            process = True
#
#        # If relevant gait cycle complete, run analysis function and reset arrays
#        if process:
#            self.hr = self.process_event()
#            self.saved_output_vars.append(self.hr)
#            self.current_period = []
#
#        # Return most recent calculated variable. If start of program and no calculations yet, return -1
#        return self.hr