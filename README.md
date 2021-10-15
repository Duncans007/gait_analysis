# Gait Analysis Functions

gait_analysis is a set of python classes for signal processing, primarily used for human gait analysis.

The package currenly only contains recursive analysis.

## Usage

Import functions using `from RecursionAnalysis import RecursionAnalysis`

Outputs HTML file including all charts and some relevant numbers.

## Minimum Working Example

```python
from RecursionAnalysis import RecursionAnalysis

filename = 'compiled_graphs.html'
chart_title = 'Title of Output Document'

analyzer = RecursionAnalysis(4, 5, 5)
analyzer.analyze_dataset(input_array, filename=filename, title=chart_title)
```
