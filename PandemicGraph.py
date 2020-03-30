#PandemicGraph.py
from PIL import Image, ImageDraw, ImageFont
import os, datetime
from Pandemic_config import GRAPH_FILE_NAME, GRAPH_FILE_EXT, GRAPH_MARGINS, GRAPH_DIM

class Graph:
    
    def _find_range(self):
        self.width, self.height = GRAPH_DIM
        self.x_range = [GRAPH_MARGINS[0][0], GRAPH_MARGINS[1][0]]
        self.y_range = [GRAPH_MARGINS[0][1], GRAPH_MARGINS[1][1]]

    def _compile_datapoints(self):
        self.datapoints = {i : [] for i in self.legend}
        for i in self.data:
            for j in i:
                if j in self.legend:
                    self.datapoints[j].append(i[j])

    def _determine_fps(self):
        self.fps = 0
        for i in self.data:
            if i["frames"] > self.fps and i["days"] == 0:
                self.fps = i["frames"]
            else:
                self.key_frame = self.data[-1]["frames"] % self.fps
                break


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
        self.image = Image.new(mode = 'RGB', size = (self.width, self.height), color=(253,249,245))
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
        xdim = self.draw.textsize("Nodes", font=self.font)
        self.draw.text((x[0] - xdim[0]/2, y[0] - 40), "Nodes", font=self.font, fill=(0,0,0), anchor='center')
        ydim = self.draw.textsize("Days", font=self.font)
        self.draw.text((x[1] + 20, y[1] - ydim[1]/2), "Days", font=self.font, fill=(0,0,0), anchor='center')
    
    def _draw_graph_lines(self):
        self.drawn_points = {}
        for i in self.datapoints:
            self.drawn_points[i] = []
            last_point = False
            color = tuple(self.legend[i])
            n_points = len(self.datapoints[i])
            points_iter = 0
            dx = self.x_high - self.key_frame
            x_incr = (self.x_range[1] - self.x_range[0])/(dx)
            y_incr = (self.y_range[1] - self.y_range[0])/(self.y_high - self.y_low)
            for j, k in zip(self.datapoints[i], range(n_points)):
                if self.data[k]["frames"] % self.fps == self.key_frame:
                    p1 = last_point
                    p2 = (x_incr*points_iter + self.x_range[0], (self.y_high - j)*y_incr + self.y_range[0])
                    if last_point:
                        line = [p1, p2]
                        self.draw.line(line, fill = color, width = 4)
                    last_point = p2
                    points_iter += self.fps
                    self.drawn_points[i].append((p2[0], p2[1], j))

    def _number_xaxis(self):
        n = 5
        x = self.x_range
        y = self.y_range
        datasets = []
        for i in self.drawn_points:
            datasets.append(self.drawn_points[i])
        if len(datasets[0]) < 10:
            n = int(len(datasets[0])/2)
        dx = (x[1] - x[0])/n
        for i in range(n + 1):
            curx = i*dx
            if i not in (0, n):
                line = [(x[0] + curx, y[1] + 10), (x[0] + curx, y[1] - 10)]
                self.draw.line(line, fill ="black", width = 2)
            days = "{0:.2f}".format((len(datasets[0]) - 1)*i/(n))
            dim = self.draw.textsize(str(days), font=self.font)
            coord = (x[0] + curx - dim[0]/2, y[1] + 30 - dim[1]/2)
            self.draw.text(coord, days, font=self.font, fill=(0,0,0), anchor='center')

    def _number_yaxis(self):
        n = 5
        x = self.x_range
        y = self.y_range
        datasets = []
        for i in self.drawn_points:
            datasets.append(self.drawn_points[i])
        ymax, ymin = datasets[0][0][2], datasets[0][0][2]
        for i in datasets:
            for j in i:
                if j[2] > ymax:
                    ymax = j[2]
                if j[2] < ymin:
                    ymin = j[2]
        if ymax - ymin < 10:
            n = int((ymax - ymin)/2)
        dy = (y[1] - y[0])/n
        for i in range(n + 1):
            cury = i*dy
            if i not in (0, n):
                line = [(x[0] + 10, y[1] - cury), (x[0] - 10, y[1] - cury)]
                self.draw.line(line, fill ="black", width = 2)
            nodes = "{0:.2f}".format(ymin + ymax*i/n)
            dim = self.draw.textsize(str(nodes), font=self.font)
            coord = (x[0] - 50 - dim[0]/2, y[1] - cury - dim[1]/2)
            self.draw.text(coord, nodes, font=self.font, fill=(0,0,0), anchor='center')


    def _make_legend(self):
        newfont = ImageFont.truetype(font="cambria", size=14)
        #dim = self.draw.textsize(str(name), font=newfont)
        #coord = (0, ycoord - dim[1]/2)
        #self.draw.text(coord, name, font=newfont, fill=(0,0,0), anchor='center')
        for i, j in zip(self.legend, range(len(self.legend))):
            ycoord = 50 + j*50
            name, color = i, tuple(self.legend[i])
            line = [(20, ycoord + 10), (130, ycoord + 10)]
            self.draw.line(line, fill =color, width = 2)
            dim = self.draw.textsize(str(name), font=newfont)
            coord = (20, ycoord - dim[1]/2)
            self.draw.text(coord, name, font=newfont, fill=(0,0,0), anchor='center')

    def _make_final_value(self):
        newfont = ImageFont.truetype(font="cambria", size=14)
        #dim = self.draw.textsize(str(name), font=newfont)
        #coord = (0, ycoord - dim[1]/2)
        #self.draw.text(coord, name, font=newfont, fill=(0,0,0), anchor='center')
        for i, j in zip(self.legend, range(len(self.legend))):
            ycoord = 50 + j*50
            final_value = str(self.data[-1][i])
            name, color = str(i) + ": " + final_value, tuple(self.legend[i])
            line = [(self.x_range[1] + 20, ycoord + 10), (self.x_range[1] + 130, ycoord + 10)]
            self.draw.line(line, fill =color, width = 2)
            dim = self.draw.textsize(name, font=newfont)
            coord = (self.x_range[1] + 20, ycoord - dim[1]/2)
            self.draw.text(coord, name, font=newfont, fill=(0,0,0), anchor='left')

    def _save_file(self):
        i = 0
        now = datetime.datetime.now()
        timestamp = "--%s-%s-%s--%s-%s--" % (now.year, now.month, now.day, now.hour, now.minute)
        file_n = GRAPH_FILE_NAME + timestamp + str(i) + GRAPH_FILE_EXT
        while os.path.isfile(os.getcwd() + file_n):
            i += 1
            file_n = GRAPH_FILE_NAME + timestamp + "_" + str(i) + GRAPH_FILE_EXT
        self.image.save(os.getcwd() + file_n)

    def __init__(self, data, legend):
        self.data = data
        self.legend = legend
        self.font = ImageFont.truetype(font="cambria", size=24)
        if self.data[-1]["days"] != 0:
            self._find_range()
            self._determine_fps()
            self._compile_datapoints()
            self._find_endpoints()
            self._create_image()
            self._draw_graph_lines()
            self._draw_axises()
            self._number_xaxis()
            self._number_yaxis()
            self._make_legend()
            self._make_final_value()
            self._save_file()