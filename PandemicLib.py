#PandemicLib.py
import pyglet
import math
import random
import MultiNodes
from Pandemic_config import *
from collections import Counter

class Pandemic:
    node_data = {"healthy" : {"color" : HEALTHY_COLOR, "speed" : HEALTHY_SPEED, "radius" : HEALTHY_RADIUS, "amount" : HEALTHY_NODES},
             "infected" : {"color" : SICK_COLOR, "speed" : SICK_SPEED, "radius" : SICK_RADIUS, "amount" : SICK_NODES}}

    def _generateNodes(self, w, h, node_spec, status):
        for _ in range(node_spec["amount"]):
            angle = random.random()*2*math.pi
            h_speed = node_spec["speed"]
            i_speed = (h_speed[1] - h_speed[0])*random.random()
            i_speed += h_speed[0]
            xs = math.cos(angle)*i_speed
            ys = math.sin(angle)*i_speed
            color = node_spec["color"]
            #color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            pos = [random.randint(0, w), random.randint(0, h)]
            speed = (xs, ys)
            radius = node_spec["radius"]
            self.nodes.AddNode(speed, color, radius, pos)
            risk_group = True
            if random.random() > RISK_GROUP_PORTION:
                risk_group = False
            self.node_status.append({"status" : status, "days sick" : 0, "risk group" : risk_group, 
                                     "serious" : False, "in treatment" : False, "days in treatment" : 0})
            self.status_count[status] += 1
            


    
    def __init__(self, w, h, caption):
        self.node_status = []
        self.status_count = {}
        self.d_time = 1.0 / WIN_FPS
        self.caption = caption
        self.win = (w, h)
        #self.infected = []
        self.nodes = MultiNodes.MultiNodes((w, h))
        self.nodes.list_overlaps = True
        self.nodes.active_collisions = COLLISIONS
        self.nodes.draw_collisions = DRAW_COLLISIONS
        self.status_count["healthy"] = 0
        self._generateNodes(w, h, self.node_data["healthy"], "healthy")
        self.status_count["infected"] = 0
        self._generateNodes(w, h, self.node_data["infected"], "infected")
        self.status_count["dead"] = 0
        self.status_count["immune"] = 0
        self.status_count["days"] = 0
        self.status_count["frames"] = 0
        self.status_count["serious in treatment"] = 0
        self.status_count["serious without treatment"] = 0
        self.status_count["serious total"] = 0

    def _infection(self, overlaps):
        status = self.node_status
        nodes = self.nodes
        node_data = self.node_data
        status_count = self.status_count
        for i in overlaps:
            factor = self.node_data["infected"]["speed"][1]/self.node_data["healthy"]["speed"][1]
            combo_status = tuple(status[j]["status"] for j in i)
            if combo_status[0] == "infected":
                if combo_status[1] == "healthy":
                    if 1 - random.random() < INFECTION_CHANCE:
                        status[i[1]]["status"] = "infected"
                        nodes.nodes[i[1]].data["color"] = node_data["infected"]["color"]
                        nodes.nodes[i[1]].data["speed"] = [nodes.nodes[i[1]].data["speed"][0]*factor, 
                                                                nodes.nodes[i[1]].data["speed"][1]*factor]
                        status_count["infected"] += 1
                        status_count["healthy"] += -1
            elif combo_status[1] == "infected":
                if combo_status[0] == "healthy":
                    if 1 - random.random() < INFECTION_CHANCE:
                        status[i[0]]["status"] = "infected"
                        nodes.nodes[i[0]].data["color"] = node_data["infected"]["color"]
                        nodes.nodes[i[0]].data["speed"] = [nodes.nodes[i[0]].data["speed"][0]*factor, 
                                                                nodes.nodes[i[0]].data["speed"][1]*factor]
                        status_count["infected"] += 1
                        status_count["healthy"] += -1

    def _serious(self):
        nodes = self.nodes
        node_status = self.node_status
        status_count = self.status_count
        for i, j in zip(node_status, range(len(node_status))):
            isrisk = i["risk group"]
            if not i["serious"] and i["status"] == "infected" and i["days in treatment"] == 0:
                if random.random() < SERIOUSLY_SICK_CHANCE*(isrisk == False) + SERIOUSLY_SICK_CHANCE_RISK_GROUP*isrisk:
                    i["serious"] = True
                    status_count["serious total"] += 1
                    if status_count["serious in treatment"] < TREATMENT_SPOTS:
                        status_count["serious in treatment"] += 1
                        nodes.nodes[j].data["color"] = IN_TREATMENT_COLOR
                        nodes.nodes[j].data["speed"] = IN_TREATMENT_SPEED
                        i["in treatment"] = True
                    else:
                        status_count["serious without treatment"] += 1
                        nodes.nodes[j].data["color"] = SERIOUSLY_SICK_COLOR
                        nodes.nodes[j].data["speed"] = SERIOUS_SPEED
                else:
                    if random.random() < LETHALITY*(isrisk == False) + \
                                         RISK_GROUP_LETHALITY*isrisk:
                        i["status"] = "dead"
                        status_count["dead"] += 1
                        nodes.nodes[j].data["color"] = DEAD_COLOR
                        nodes.nodes[j].data["speed"] = DEAD_SPEED
                        status_count["infected"] -= 1
            elif i["serious"] and i["status"] not in ("healthy", "dead", "immune"):
                if i["in treatment"] == False:
                    if random.random() < SERIOUS_LETHALITY_WITHOUT_TREATMENT*(isrisk == False) + \
                                         SERIOUS_LETHALITY_WITHOUT_TREATMENT_RISK_GROUP*isrisk:
                        i["status"] = "dead"
                        status_count["dead"] += 1
                        nodes.nodes[j].data["color"] = DEAD_COLOR
                        nodes.nodes[j].data["speed"] = DEAD_SPEED
                        status_count["infected"] -= 1
                        status_count["serious without treatment"] += -1
                        status_count["serious total"] -= 1
                    else:
                        if status_count["serious in treatment"] < TREATMENT_SPOTS:
                            status_count["serious in treatment"] += 1
                            status_count["serious without treatment"] += -1
                            nodes.nodes[j].data["color"] = IN_TREATMENT_COLOR
                            nodes.nodes[j].data["speed"] = IN_TREATMENT_SPEED
                            i["in treatment"] = True
                else:
                    i["days in treatment"] += 1/WIN_FPS
                    if random.random() < RISK_GROUP_LETHALITY*(isrisk == False) + \
                                         RISK_GROUP_LETHALITY*isrisk:
                        i["status"] = "dead"
                        status_count["dead"] += 1
                        nodes.nodes[j].data["color"] = DEAD_COLOR
                        nodes.nodes[j].data["speed"] = DEAD_SPEED   
                        status_count["infected"] -= 1
                        status_count["serious in treatment"] += -1
                        status_count["serious total"] -= 1
                    else:
                        if i["days in treatment"] > TREATMENT_DAYS:
                            #status_count["infected"] += 1
                            status_count["serious in treatment"] += -1
                            status_count["serious total"] -= 1
                            h_speed = SICK_SPEED
                            i_speed = (h_speed[1] - h_speed[0])*random.random()
                            i_speed += h_speed[0]
                            angle = random.random()*2*math.pi
                            xs = math.cos(angle)*i_speed
                            ys = math.sin(angle)*i_speed
                            nodes.nodes[j].data["speed"] = (xs, ys)
                            nodes.nodes[j].data["color"] = SICK_COLOR
                            i["status"] = "infected"
                            i["serious"] = False

    def _update_status(self, overlaps):
        self._serious()
        self._infection(overlaps)
        node_status = self.node_status
        nodes = self.nodes
        status_count = self.status_count
        status_count["frames"] += 1
        status_count["days"] = int(status_count["frames"]/WIN_FPS)
        for i, j in zip(node_status, range(len(node_status))):
            if i["status"] == "infected":
                if i["days sick"] < TIME_TILL_IMMUNE:
                    i["days sick"] += 1.0/WIN_FPS
                else:
                    status_count["infected"] += -1
                    if i["serious"]:
                        status_count["serious total"] -= 1
                        i["serious"] = False
                        if i["in treatment"]:
                            i["in treatment"] = False
                            status_count["serious in treatment"] -= 1
                        else:
                            status_count["serious without treatment"] -= 1
                    i["status"] = "immune"
                    status_count["immune"] += 1
                    nodes.nodes[j].data["color"] = IMMUNE_COLOR
                    nodes.nodes[j].data["speed"] = IMMUNE_SPEED

    

    def draw(self, dt, func, win):
        if not func.done:
            win.clear()
            overlaps = func.newframe()
            self._update_status(overlaps)
            self._status_draw()
    
    def _status_init(self):
        window = self.window
        self.status_text = []
        for i in range(len(self.status_count)):
            newlab = pyglet.text.Label('',
                                       font_name='Times New Roman',
                                       font_size=12,
                                       x=5, y=window.height - 16*i,
                                       anchor_x='left', anchor_y='top', color=[255, 255, 255, 200])
            self.status_text.append(newlab)
    
    def _status_draw(self):
        status_count = self.status_count
        status_text = self.status_text
        for i, j in zip(status_count, status_text):
            if i != "frames":
                out_str = str(i) + ": " + str(status_count[i]) + '\n'
                j.text = str(out_str)
                j.draw()

    def Start(self):
        w, h = self.win
        self.window = pyglet.window.Window(w, h, visible=False, caption=self.caption, vsync=0)
        self.window.set_visible()
        self.window.double_buffer = False
        self.nodes.data["resolution"] = NODE_RES
        self.window.on_mouse_press = self.nodes.on_mouse_press
        self._status_init()
        pyglet.clock.schedule_interval(self.draw, self.d_time, self.nodes, self.window)
        pyglet.app.run()
