#PandemicGraph.py
from PIL import Image, ImageDraw
import os
from Pandemic_config import GRAPH_FILE_NAME, GRAPH_FILE_EXT, GRAPH_MARGINS, GRAPH_WIDTH_TO_HEIGHT, GRAPH_MIN_DIM

class Graph:
    
    def _find_range(self):
        x0 = len(self.data)*(GRAPH_MARGINS/100)
        x1 = len(self.data)*(1 + (GRAPH_MARGINS)/100)
        self.x_range = (x0, x1)
        y0 = x0
        y1 = x1/GRAPH_WIDTH_TO_HEIGHT
        self.y_range = (y0, y1)
        self.width = int(len(self.data)*(1 + 2*(GRAPH_MARGINS)/100))
        self.height = int(len(self.data)*(1/GRAPH_WIDTH_TO_HEIGHT + 2*(GRAPH_MARGINS)/100))
        if self.width < GRAPH_MIN_DIM[0]:
            self.width, self.height = GRAPH_MIN_DIM
            margin = self.width*GRAPH_MARGINS/100, self.height*GRAPH_MARGINS/100, 
            self.x_range = [margin[0], self.width - margin[0]]
            self.y_range = [margin[1], self.height - margin[1]]
    
    def _cut_extra_data(self):
        new_data = []
        temp_data = []
        last_day = 0
        for i in self.data:
            temp_data.append(i)
            if i["days"] != last_day:
                last_day = i["days"]
                new_data += temp_data
                temp_data = []
        self.data = new_data

    def _compile_datapoints(self):
        self.datapoints = {i : [] for i in self.legend}
        for i in self.data:
            for j in i:
                if j in self.legend:
                    self.datapoints[j].append(i[j])

    def _find_endpoints(self):
        self.x_low = self.data[0]["frames"]
        self.x_high = self.data[-1]["frames"]
        y_low = list(self.datapoints.values())[0][0]
        y_high = list(self.datapoints.values())[0][0]
        for i in self.datapoints:
            for j in self.datapoints[i]:
                if j > y_high:
                    y_high = j
                elif j < y_low:
                    y_low = j
        self.y_high = y_high
        self.y_low = y_low
    
    def _create_image(self):
        self.image = Image.new(mode = 'RGB', size = (self.width, self.height), color=(255,255,255))
        self.draw = ImageDraw.Draw(self.image)
    
    def _draw_axises(self):
        x = self.x_range
        y = self.y_range
        y_line = [(x[0], y[1]), (x[0], y[0])]
        x_line = [(x[0], y[1]), (x[1], y[1])]
        y_arrow1 = [(x[0], y[0]), (x[0] - 10, y[0] + 10)]
        y_arrow2 = [(x[0], y[0]), (x[0] + 10, y[0] + 10)]
        x_arrow1 = [(x[1], y[1]), (x[1] - 10, y[1] - 10)]
        x_arrow2 = [(x[1], y[1]), (x[1] - 10, y[1] + 10)]
        draw_lines = [x_line, y_line, x_arrow1, x_arrow2, y_line, y_arrow1, y_arrow2]
        for i in draw_lines:
            self.draw.line(i, fill ="black", width = 2)
    
    def _draw_graph_lines(self):
        for i in self.datapoints:
            last_point = False
            last_day = -1
            color = tuple(self.legend[i])
            n_points = len(self.datapoints[i])
            x_incr = (self.x_range[1] - self.x_range[0])/(self.x_high - self.x_low)
            y_incr = (self.y_range[1] - self.y_range[0])/(self.y_high - self.y_low)
            for j, k in zip(self.datapoints[i], range(n_points)):
                new_day = self.data[k]["days"]
                if last_day != new_day:
                    last_day = new_day
                    p1 = last_point
                    p2 = (x_incr*k + self.x_range[0], (self.y_high - j)*y_incr + self.y_range[0])
                    if last_point:
                        line = [p1, p2]
                        self.draw.line(line, fill = color, width = 2)
                    last_point = p2
    
    def _save_file(self):
        i = 0
        file_n = GRAPH_FILE_NAME + str(i) + GRAPH_FILE_EXT
        while os.path.exists(file_n):
            i += 1
            file_n = GRAPH_FILE_NAME + str(i) + GRAPH_FILE_EXT
        self.image.save(os.getcwd() + file_n)
        self.image.show()



    def __init__(self, data, legend):
        self.data = data
        self.legend = legend
        self._find_range()
        self._cut_extra_data()
        self._compile_datapoints()
        self._find_endpoints()
        self._create_image()
        self._draw_graph_lines()
        self._draw_axises()
        self._save_file()