# Gait Analysis Functions

gait_analysis is a set of python classes for signal processing, primarily used for human gait analysis.

The package currenly only contains recursive analysis and harmonic ratio analysis.

## Dependencies

- plotly express
- pandas
- numpy
- scipy

## Usage

### Class: RecursionAnalysis()

Takes dataset as input, and iterates over each frame while testing against prior frames for similarities and patterns.
Compiles into recursion plots, then analyses to show diagonal lines over time as a quantitative output.

Create Object:
```python
analyzer = RecursionAnalysis(lag, dim, rad, ref=100)
# lag -> time lag in raw frames
# dim -> number of consecutive time-lag datapoints to analyze
# rad -> distance limit for point similarity
# ref -> total refresh time in frames. Only necessary for live application.
```

Analyze Dataset:
```python
analyzer.analyze_dataset(dataset, filename='html_file.html', title='Recursion Analysis of Dataset')
```

Minimum Working Example:

```python
from RecursionAnalysis import RecursionAnalysis

filename = 'compiled_graphs.html'
chart_title = 'Title of Output Document'

analyzer = RecursionAnalysis(4, 5, 5)
analyzer.analyze_dataset(input_array, filename=filename, title=chart_title)
```

### Class: HarmonicRatio()

Takes dataset as input, and iterates over frames to analyse the data in chunks, or "windows."
These windows are converted to frequencies using rfft, then the first ten even and odd harmonics are summed and divided to obtain the harmonic ratio over time.

Create Object:
```python
analyzer = HarmonicRatio(dir, freq, rw)
    # dir -> "x"(AP), "y"(V), "z"(ML)
    # freq -> frequency of signal in Hz
    # rw -> read/write permissions, same as used in open(). Defaults to overwriting (w+). Appending is a+
```

Analyze Dataset:
```python
analyze_dataset(self, dataset, window_size, window_delta, filename=""):
    # dataset -> single dimension time values of signal
    # window_size -> length of window for each individual harmonic analysis
    # window_delta -> increment of window after each analysis
    # filename -> .HTML file for charts to output after each run
```

Minimum Working Example:

```python
from HarmonicRatio import HarmonicRatio

signal_frequency = 50 #Hz
window_size = 80
window_delta = 1
filename = 'hr_graphs.html'

analyzer = HarmonicRatio("x", signal_frequency, "w+")
analyzer.analyze_dataset(input_array, window_size, window_delta, filename=filename)
```