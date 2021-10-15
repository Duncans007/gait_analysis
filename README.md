# Gait Analysis Functions

gait_analysis is a set of python classes for signal processing, primarily used for human gait analysis.

The package currenly only contains recursive analysis.

## Dependencies

- plotly express
- pandas
- numpy

## Usage

Import:
```python
from RecursionAnalysis import RecursionAnalysis
```

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
analyzer.analyze_dataset(dataset, filename='compiled_charts.html', title='Recursion Analysis of Dataset')
```

Saves output to HTML file, including all charts and some relevant numbers. Returns 0.

## Minimum Working Example

```python
from RecursionAnalysis import RecursionAnalysis

filename = 'compiled_graphs.html'
chart_title = 'Title of Output Document'

analyzer = RecursionAnalysis(4, 5, 5)
analyzer.analyze_dataset(input_array, filename=filename, title=chart_title)
```
