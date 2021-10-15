import plotly.express as px
import pandas as pd
from numpy import zeros, mean
from math import sqrt


class RecursionAnalysis():
    ## Variables to Initialize:
    # lag -> time lag in raw frames
    # dim -> number of consecutive time-lag datapoints to analyze
    # rad -> distance limit for point similarity
    # ref -> total refresh time in frames. Only necessary for live application.

    def __init__(self, lag, dim, rad, ref=100):
        # Input initializations
        self.time_lag = lag
        self.dimensions = dim
        self.radius = rad
        self.refresh_time = ref

        # Other variable initializations
        self.saved_ra_points = []
        self.saved_input_points = []
        self.max_input_points = (self.dimensions * self.time_lag)

        # Compute necessary time-lagged indices to grab
        self.need_indices = []
        for i in range(0, dim):
            #computes last point, then TIMELAG before it for DIMENSION numbers
            self.need_indices.append(self.max_input_points - ( i * self.time_lag ))


    def analyze_dataset(self, dataset, filename='compiled_charts.html', title='Recursion Analysis of Dataset'):
        ## Iterate through larger dataset to give analyzer data, then plot when done
        # dataset -> complete array of signal over time
        # filename -> output file for charts, overwrites on run
        # title -> output document title

        saved_ra_points = []
        for x in range(self.max_input_points, len(dataset)):
            saved_ra_points.append(self.get_timelag_points(dataset[x-self.max_input_points:x]))

        with open(filename, 'w+') as f:
            f.write(f"<h1>{title}</h1>\n")
            self.plot_line(dataset[self.max_input_points::], f, title='Plotted Signal')
            self.recursion_plot(saved_ra_points, f)

        return 0


    def insert_pt(self, datapt):
        ## Add single points to array, then store them long enough to use as time-lagged points.
        # datapt -> single frame of time-based data

        #add single points to array
        self.saved_input_points.append(datapt)

        #can't start calculating if there's not enough datapoints ¯\_(ツ)_/¯
        if len(self.saved_input_points) > self.max_input_points:
            #remove first value of the array to keep it from getting too long? is it algorithmically quicker to not?
            self.saved_input_points.pop(0)

            #take indices of time-lagged points and save to array
            timelag_values = self.get_timelag_points(self.saved_input_points)
            self.saved_ra_points.append(timelag_values)

        return 0


    def get_timelag_points(self, dataset):
        ## Pull points from overall array with timelag separation
        # dataset -> containing just enough values to pull from current to farthest back time_lag

        #initialize storage array
        grab_values = []

        #iterate over DIMENSION predetermined indices at TIME_LAG intervals.
        for idx in self.need_indices:
            grab_values.append(dataset[idx-1])

        return grab_values


    def recursion_plot(self, ra_points, f):
        ## Analyze dimensional points to draw 2D recursion plot of those satisfying the criteria
        # ra_points -> Dimensional recursion analysis points
        # f -> file object to save output to

        #unzip data from current form (array of [x,y] points) into heatmap (square array)
        #TODO: find quick way to mirror table halves (add each array to the end of the other?) for display

        #initialize sqare array
        rp = []

        #iterate twice over the length of saved points array, so that each point checks against every other
        #TODO: OPTIMIZE ALGORITHMICALLY
        for i in range(len(ra_points)):
            newline = zeros(len(ra_points))
            for j in range(i, len(ra_points)):

                #initialize distances to store a point-to-point distance for each dimension
                distances = []
                for dim in range(0,self.dimensions):
                    distances.append( (ra_points[i][dim] - ra_points[j][dim])**2 )

                #sums dimensional disatances to get magnitude of distance, marks positive if large enough
                if sqrt(sum(distances)) <= self.radius:
                    newline[j] = 1

            rp.append(newline)

        #get relevant RQA values
        avgL, maxL, over_timeL = self.line_analysis(rp)

        #generate recursion plot figure
        fig = px.imshow(rp, color_continuous_scale='gray_r', origin="lower",
                        title=f"Recursion Plot")

        #save numbers to HTML output
        f.write(f"<h2>Lag={self.time_lag}, Dim={self.dimensions}, Rad={self.radius}</h2>\n")
        f.write(f"<h2>Avg Line: {round(avgL,3)}, Max Line: {maxL}</h2>\n")
        #save recursion plot to HTML output
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        #plot average line length over time and save to HTML output
        self.plot_line(over_timeL, f, title="Measure of Stability via Average Diagonal Line Length at Time t")

        return rp


    def line_analysis(self, rp):
        ## Calculate diagonal lines in bottom half of recursion plot
        # rp -> recursion plot heatmap

        line_length = 0
        line_lengths = []

        arr_total_len_by_time = zeros(len(rp))
        arr_num_entries_by_time = zeros(len(rp))
        arr_avg_len_by_time = zeros(len(rp))

        #Create starting point for each diagonal analysis
        for x_start in range(1, len(rp)):

            #using start point, create incrementing variable
            x = x_start

            #increment y variable, and use same for loop to increment x variable simultaneously for diagonal movement
            for y in range(0, len(rp)-x):

                #Check slot for 1, if 1 then increment line length
                if rp[y][x] == 1:
                    line_length += 1

                    #Alternate to complete-line-saving commented below
                    arr_total_len_by_time[x] += min(line_length, self.refresh_time)
                    arr_num_entries_by_time[x] += 1

                #If 0, check if line length has anything recorded. If it does, reset.
                else:
                    if line_length > 0:
                        line_lengths.append(line_length)

                        #back-saves line length to all times that the line occurred over
                        #for back_x in range(x-line_length, x):
                        #    arr_total_len_by_time[back_x] += line_length
                        #    arr_num_entries_by_time[back_x] += 1

                        line_length = 0
                x += 1

            #Checks for hanging line length after loop is finished executing, and resets
            if line_length > 0:
                line_lengths.append(line_length)
                for back_x in range(x - line_length, x):
                    arr_total_len_by_time[back_x] += line_length
                    arr_num_entries_by_time[back_x] += 1
                line_length = 0

        #Calculate average and maximum line lengths
        avg_line = mean(line_lengths)
        max_line = max(line_lengths)

        #Calculate average line length for each individual time step
        for i in range(0,len(arr_total_len_by_time)):
            if arr_num_entries_by_time[i] != 0:
                arr_avg_len_by_time[i] = arr_total_len_by_time[i] / arr_num_entries_by_time[i]

        return avg_line, max_line, arr_avg_len_by_time


    def plot_line(self, y, f, title=''):
        ## Generate line plot of a single-dimension signal over time
        # y -> 1d signal values
        # f -> file object for saving
        # title -> plot title

        x = list(range(0,len(y)))
        df = pd.DataFrame(dict(
            t=x,
            y=y
        ))
        fig = px.line(df, x="t", y="y", title=title)
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write("<hr>\n<hr>\n")

        return 0