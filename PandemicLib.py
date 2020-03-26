#PandemicLib.py
import pyglet
import math
import random
import MultiNodes
from Pandemic_config import *
from collections import Counter

class Pandemic:
    not_handle = ("healthy", "dead", "immune")
    node_data = {"healthy" : {"color" : HEALTHY_COLOR, "speed" : HEALTHY_SPEED, "radius" : HEALTHY_RADIUS, "amount" : HEALTHY_NODES},
                 "infected" : {"color" : INFECTED_COLOR, "speed" : INFECTED_SPEED, "radius" : INFECTED_RADIUS, "amount" : INFECTED_NODES},
                 "immune" : {"color" : IMMUNE_COLOR, "speed" : IMMUNE_SPEED, "radius" : IMMUNE_RADIUS, "amount" : IMMUNE_NODES}
             }

    def _node_list(self, status):
        gen_list = []
        node_status = self.node_status
        for i in range(len(node_status)):
            if node_status[i]["status"] == status:
                gen_list.append(i)
        return gen_list

    def _generateNodes(self, w, h, node_spec, status):
        for _ in range(node_spec["amount"]):
            angle = random.random()*2*math.pi
            h_speed = node_spec["speed"]
            i_speed = (h_speed[1] - h_speed[0])*random.random()
            i_speed += h_speed[0]
            xs = math.cos(angle)*i_speed
            ys = math.sin(angle)*i_speed
            color = node_spec["color"]
            pos = [random.randint(0, w), random.randint(0, h)]
            speed = (xs, ys)
            radius = node_spec["radius"]
            self.nodes.AddNode(speed, color, radius, pos)
            risk_group = True
            if random.random() > RISK_GROUP_PORTION:
                risk_group = False
            self.node_status.append({"status" : status, "days sick" : 0, "risk group" : risk_group, 
                                     "serious" : False, "in treatment" : False, "days in treatment" : 0, 
                                     "current seed" : 0, "speed" : (xs, ys), "self isolated" : False})
            self.status_count[status] += 1
            


    def _vaccinate(self):
        for i, j in zip(range(len(self.nodes.nodes)), self.node_status):
            if j["status"] == "healthy":
                if self.status_count["immune"]/len(self.nodes.nodes) < PERCENTAGE_VACCINATED/100:
                    j["status"] = "immune"
                    self.status_count["immune"] += 1
                    self.status_count["healthy"] -= 1
                    self.nodes.nodes[i].data["color"] = IMMUNE_COLOR
                    self.nodes.nodes[i].data["speed"] = IMMUNE_SPEED

    def _self_isolate(self):
        for i, j in zip(range(len(self.nodes.nodes)), self.node_status):
            if j["status"] == "healthy":
                if self.status_count["immune"]/len(self.nodes.nodes) < PERCENTAGE_SOCIAL_DISTANCING/100:
                    j["self isolated"] = True
                    self.status_count["immune"] += 1
                    angle = random.random()*2*math.pi
                    h_speed = SOCIAL_DISTANCING_SPEED
                    i_speed = (h_speed[1] - h_speed[0])*random.random()
                    i_speed += h_speed[0]
                    xs = math.cos(angle)*i_speed
                    ys = math.sin(angle)*i_speed
                    self.nodes.nodes[i].data["speed"] = (xs, ys)
                    j["speed"] = (xs, ys)

    def __init__(self, w, h, caption):
        self.node_status = []
        self.d_time = 1.0 / WIN_FPS
        self.caption = caption
        self.win = (w, h)
        self.nodes = MultiNodes.MultiNodes((w, h))
        self.nodes.list_overlaps = True
        self.nodes.active_collisions = COLLISIONS
        self.nodes.draw_collisions = DRAW_COLLISIONS
        counts = "healthy", "infected", "dead", "immune", "days", "frames", "serious in treatment", \
                "serious without treatment", "serious total", "self isolated"
                 
        self.status_count = {i: 0 for i in counts}
        self._generateNodes(w, h, self.node_data["healthy"], "healthy")
        self._generateNodes(w, h, self.node_data["infected"], "infected")
        self._vaccinate()
        self._self_isolate()

    def _update_current_seed(self, i):
        i["current seed"] = random.random()
    
    def _update_serious(self, i, j):
        isrisk = i["risk group"]
        seed = i["current seed"]
        if not i["serious"] and i["status"] == "infected":
            if seed < SERIOUSLY_SICK_CHANCE*(isrisk == False) + SERIOUSLY_SICK_CHANCE_RISK_GROUP*isrisk:
                i["serious"] = True
                self.status_count["serious total"] += 1
                self.nodes.nodes[j].data["color"] = SERIOUSLY_INFECTED_COLOR
                self.nodes.nodes[j].data["speed"] = SERIOUS_SPEED
    
    def _update_treatment_status(self, i, j):
        serious = i["serious"]
        in_treatment = i["in treatment"]
        if serious and not in_treatment:
            if self.status_count["serious in treatment"] < TREATMENT_SPOTS:
                self.status_count["serious in treatment"] += 1
                self.nodes.nodes[j].data["color"] = IN_TREATMENT_COLOR
                self.nodes.nodes[j].data["speed"] = IN_TREATMENT_SPEED
                i["in treatment"] = True
            else:
                self.status_count["serious without treatment"] += 1
        elif serious and in_treatment:
            i["days in treatment"] += 1/WIN_FPS
            if i["days in treatment"] > TREATMENT_DAYS:
                self.status_count["serious in treatment"] += -1
                self.status_count["serious total"] += -1
                self.nodes.nodes[j].data["color"] = INFECTED_COLOR
                self.nodes.nodes[j].data["speed"] = i["speed"]
                i["serious"] = False
                i["in treatment"] = False

    def _update_immune(self, i, j):
        nodes = self.nodes
        status_count = self.status_count
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
                        status_count["serious in treatment"] += -1
                    else:
                        status_count["serious without treatment"] += -1
                i["status"] = "immune"
                status_count["immune"] += 1
                nodes.nodes[j].data["color"] = IMMUNE_COLOR
                nodes.nodes[j].data["speed"] = IMMUNE_SPEED

    def _handle_dead(self, infected):
        node_status = self.node_status
        status_count = self.status_count
        nodes = self.nodes
        for i in infected:
            j = node_status[i]
            isrisk = j["risk group"]
            in_treatment = j["in treatment"]
            serious = j["serious"]
            seed = j["current seed"]
            lethality_no_threat = (SERIOUS_LETHALITY_WITHOUT_TREATMENT*(isrisk == False) + \
                                    SERIOUS_LETHALITY_WITHOUT_TREATMENT_RISK_GROUP*isrisk)*(in_treatment == False)
            lethality_normal = (LETHALITY*(isrisk == False) + RISK_GROUP_LETHALITY*isrisk)*(serious == False)
            if seed < lethality_no_threat + lethality_normal:
                j["status"] = "dead"
                nodes.nodes[i].data["color"] = DEAD_COLOR
                nodes.nodes[i].data["speed"] = DEAD_SPEED
                status_count["dead"] += 1
                status_count["infected"] -= 1
                if in_treatment:
                    status_count["serious in treatment"] += -1
                if serious:
                    self.status_count["serious total"] += -1
                    if not in_treatment:
                        status_count["serious without treatment"] += -1

    def _handle_new_infections(self, overlaps):
        status = self.node_status
        nodes = self.nodes
        node_data = self.node_data
        status_count = self.status_count
        for i in overlaps:
            h_n, i_n = None, None
            for j in i:
                if status[j]["status"] == "healthy":
                    h_n = j
                elif status[j]["status"] == "infected":
                    i_n = j
            if h_n and i_n:
                seed = status[h_n]["current seed"]
                factor = self.node_data["infected"]["speed"][1]/self.node_data["healthy"]["speed"][1]
                if seed < INFECTION_CHANCE:
                    status[h_n]["status"] = "infected"
                    nodes.nodes[h_n].data["color"] = node_data["infected"]["color"]
                    nodes.nodes[h_n].data["speed"] = [status[h_n]["speed"][0]*factor, \
                                                    status[h_n]["speed"][1]*factor]
                    status_count["infected"] += 1
                    status_count["healthy"] += -1

    def _update_status(self, overlaps, infected):
        self.status_count["serious without treatment"] = 0
        self.status_count["frames"] += 1
        self.status_count["days"] = int(self.status_count["frames"]/WIN_FPS)
        node_status = self.node_status
        for i in overlaps:
            for j in i:
                if j not in infected:
                    self._update_current_seed(node_status[j])
        for i, j in zip(node_status, range(len(node_status))):
            if i["status"]  not in self.not_handle:
                self._update_current_seed(i)
                self._update_serious(i, j)
                self._update_treatment_status(i, j)
                self._update_immune(i, j)
        self._handle_dead(infected)
        self._handle_new_infections(overlaps)

    def _update_speed(self):
        for i, j in zip(self.nodes.nodes, self.node_status):
            j["speed"] = i.data["speed"]

    def draw(self, dt, func, win):
        if not func.done:
            win.clear()
            infected, healthy = self._node_list("infected"), self._node_list("healthy")
            comp = infected, healthy
            overlaps = func.newframe(comp)
            self._update_speed()
            self._update_status(overlaps, infected)
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
