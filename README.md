# Gait Analysis Functions

gait_analysis is a set of python classes for signal processing, primarily used for human gait analysis.

The package currenly contains classes for:
- Recursive and recursion quantification analysis
- Harmonic ratio analysis
- Kalman filter for 6DoF IMU sensor fusion (roll and pitch output)
- Kalman filter for acceleration-gait fusion (walking velocity output)


## Dependencies

- plotly express
- pandas
- numpy
- scipy

## Usage


### Class: kalman_filter_6dof()

Kalman Filter for 6DoF IMU Sensor Fusion
Fuses gyroscope and accelerometer measurements for pitch and roll angles
Applicable to any IMU sensor

Create Object:
```python
filter = kalman_filter_6dof()
```

Use as a live filter (manually update):
```python
roll, pitch = filter.update([gy_x, gy_y, gy_z], [ac_x, ac_y, ac_z], sample_time)
```

Analyze Dataset:
```python
dataset = [time_arr, gy_x_arr, gy_y_arr, gy_z_arr, ac_x_arr, ac_y_arr, ac_z_arr]
roll_over_time, pitch_over_time = filter.analyze_dataset(dataset)
```

Minimum Working Example:

```python
from SensorFusion import kalman_filter_6dof

filter = kalman_filter_6dof()

dataset = [time_arr, gy_x_arr, gy_y_arr, gy_z_arr, ac_x_arr, ac_y_arr, ac_z_arr]

roll_over_time, pitch_over_time = filter.analyze_dataset(dataset)
```


### Class: kalman_filter_velocity()

Kalman Filter for Velocity
Fuses positional and acceleration values to determine subject speed
Acceleration comes from an IMU on the lower back
Position comes from BoS (Base of Support) summation over time

Create Object:
```python
filter = kalman_filter_velocity()
```

Use as a live filter (manually update):
```python
speed_current = filter.update([ac_x, ac_y, ac_z], pitch, position, sample_time)
```

Analyze Dataset:
```python
dataset = [time_arr, ac_x_arr, ac_y_arr, ac_z_arr, pitch_arr, position_arr]
speed_over_time = filter.analyze_dataset(dataset)
```

Minimum Working Example:

```python
from SensorFusion import kalman_filter_velocity

filter = kalman_filter_velocity()

dataset = [time_arr, ac_x_arr, ac_y_arr, ac_z_arr, pitch_arr, position_arr]

speed_over_time = filter.analyze_dataset(dataset)
```


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
analyzer.analyze_dataset(dataset, window_size, window_delta, filename=""):
    # dataset -> single dimension time values of signal
    # window_size -> length of window for each individual harmonic analysis
    # window_delta -> increment of window after each analysis
    # filename -> .HTML file for charts to output after each run
```

Minimum Working Example:

```python
from HarmonicRatio import HarmonicRatio

signal_frequency = 50 #Hz
window_size = 80 #Frames at a time to analyze (here, approx. 1 stride)
window_delta = 1 #Frames to move up after each analysis

analyzer = HarmonicRatio("x", 50, "w+")
analyzer.analyze_dataset(input_array, window_size, window_delta, filename='hr_graphs.html')
```
