#PandemicLib.py
import pyglet
import math
import random
import MultiNodes
from Pandemic_config import *
from PandemicGraph import Graph
from collections import Counter
import PandemicNode

class Pandemic:
    not_handle = ("healthy", "dead", "immune")
    node_data = {"healthy" : {"color" : HEALTHY_COLOR, "speed" : HEALTHY_SPEED, "radius" : HEALTHY_RADIUS, "amount" : HEALTHY_NODES},
                 "infected" : {"color" : INFECTED_COLOR, "speed" : INFECTED_SPEED, "radius" : INFECTED_RADIUS, "amount" : INFECTED_NODES}}

    def _node_list(self, status):
        gen_list = []
        p_nodes = self.p_nodes
        for i in range(len(p_nodes)):
            if p_nodes[i].data["status"] == status:
                gen_list.append(i)
        return gen_list

    def _generateNodes(self, w, h, node_spec, status):
        for _ in range(node_spec["amount"]):
            node = PandemicNode.PandemicNode(status, self.nodes, w, h)
            self.p_nodes.append(node)
            self.status_count[status] += 1
            

    def _vaccinate(self):
        p_nodes = list(self.p_nodes)
        random.shuffle(p_nodes)
        for i in p_nodes:
            if i.data["status"] == "healthy":
                if self.status_count["immune"]/len(self.p_nodes) < PERCENTAGE_VACCINATED/100:
                    i.updateStatus("immune")
                    self.status_count["immune"] += 1
                    self.status_count["healthy"] -= 1

    def _self_isolate(self):
        p_nodes = list(self.p_nodes)
        random.shuffle(p_nodes)
        for i in p_nodes:
            if i.data["status"] != "infected":
                if self.status_count["self isolated"]/len(self.p_nodes) < PERCENTAGE_SOCIAL_DISTANCING/100:
                    i.data["self isolated"] = True
                    self.status_count["self isolated"] += 1
                    i.updateSpeed(SOCIAL_DISTANCING_SPEED)

    def _practice_hygiene(self):
        p_nodes = list(self.p_nodes)
        random.shuffle(p_nodes)
        for i in p_nodes:
            if self.status_count["practicing hygiene"]/len(self.p_nodes) < PERCENTAGE_HYGIENE/100:
                i.data["practicing hygiene"] = True
                self.status_count["practicing hygiene"] += 1

    def __init__(self, w, h, caption):
        self.p_nodes = []
        self.captured_data = []
        self.d_time = 1.0 / WIN_FPS
        self.caption = caption
        self.win = (w, h)
        self.nodes = MultiNodes.MultiNodes((w, h))
        self.nodes.list_overlaps = True
        self.nodes.active_collisions = COLLISIONS
        self.nodes.draw_collisions = DRAW_COLLISIONS
        counts = "healthy", "infected", "dead", "immune", "days", "frames", "serious in treatment", \
                 "serious without treatment", "serious total", "self isolated", "practicing hygiene", \
                 "quarantined"
        self.status_count = {i: 0 for i in counts}
        self._generateNodes(w, h, self.node_data["healthy"], "healthy")
        self._generateNodes(w, h, self.node_data["infected"], "infected")
        self._vaccinate()
        self._self_isolate()
        self._practice_hygiene()

    def _update_current_seed(self, i):
        i.reSeed()
    
    def _update_serious(self, i):
        isrisk = i.data["risk group"]
        seed = i.seed["serious"]
        if not i.data["serious"] and i.data["status"] == "infected":
            if seed < SERIOUSLY_SICK_CHANCE*(isrisk == False) + SERIOUSLY_SICK_CHANCE_RISK_GROUP*isrisk \
            and i.data["days in treatment"] == 0:
                self.status_count["serious total"] += 1
                i.Serious()
    
    def _update_treatment_status(self, i):
        serious = i.data["serious"]
        in_treatment = i.data["in treatment"]
        quarantined = i.data["quarantined"]
        if serious and not in_treatment:
            if self.status_count["serious in treatment"] < TREATMENT_SPOTS:
                self.status_count["serious in treatment"] += 1
                if not quarantined:
                    self.status_count["quarantined"] += 1
                i.inTreatment()
            else:
                self.status_count["serious without treatment"] += 1
        elif serious and in_treatment:
            i.data["days in treatment"] += 1/WIN_FPS
            if i.data["days in treatment"] > TREATMENT_DAYS:
                self.status_count["serious in treatment"] += -1
                self.status_count["serious total"] += -1
                i.treatmentOver(False)

    def _update_immune(self, i):
        status_count = self.status_count
        if i.data["status"] == "infected":
            if i.data["days sick"] < TIME_TILL_IMMUNE or i.data["in treatment"]:
                i.data["days sick"] += 1.0/WIN_FPS
            else:
                status_count["infected"] += -1
                status_count["immune"] += 1
                i.treatmentOver(True)
                if i.data["quarantined"]:
                    status_count["quarantined"] += -1

    def _handle_dead(self, infected):
        p_nodes = self.p_nodes
        status_count = self.status_count
        for i in infected:
            j = p_nodes[i]
            isrisk = j.data["risk group"]
            in_treatment = j.data["in treatment"]
            serious = j.data["serious"]
            seed = j.seed["dead"]
            quarantined = j.data["quarantined"]
            lethality_no_threat = (SERIOUS_LETHALITY_WITHOUT_TREATMENT*(isrisk == False) + \
                                    SERIOUS_LETHALITY_WITHOUT_TREATMENT_RISK_GROUP*isrisk)*(in_treatment == False)
            lethality_normal = (LETHALITY*(isrisk == False) + RISK_GROUP_LETHALITY*isrisk)*(serious == False)
            if seed < lethality_no_threat + lethality_normal:
                j.kill()
                status_count["dead"] += 1
                status_count["infected"] -= 1
                if in_treatment:
                    status_count["serious in treatment"] += -1
                if quarantined:
                    status_count["quarantined"] += -1
                if serious:
                    self.status_count["serious total"] += -1
                    if not in_treatment:
                        status_count["serious without treatment"] += -1

    def _quarantine_nodes(self, infected):
        p_nodes = self.p_nodes
        status_count = self.status_count
        for i in infected:
            j = p_nodes[i]
            serious = j.data["serious"]
            quarantined = j.data["quarantined"]
            seed = j.seed["quarantined"]
            if seed < QUARANTINE_CHANCE_PERCENT/100 and not serious and not quarantined:
                j.quarantined()
                status_count["quarantined"] += 1

    def _gethygiene(self, n1, n2):
        tot_hygiene = 1
        if self.p_nodes[n1].data["practicing hygiene"]:
            tot_hygiene *= HYGIENE_FACTOR
        if self.p_nodes[n2].data["practicing hygiene"]:
            tot_hygiene *= HYGIENE_FACTOR
        return tot_hygiene
    
    def _infection_chance(self, n1, n2):
        base = INFECTION_CHANCE
        if self.p_nodes[n1].data["quarantined"]:
            base *= QUARNATINE_INFECTION_RATIO
        if self.p_nodes[n2].data["quarantined"]:
            base *= QUARNATINE_INFECTION_RATIO
        return base

    def _handle_new_infections(self, overlaps):
        p_nodes = self.p_nodes
        status_count = self.status_count
        for i in overlaps:
            h_n, i_n = None, None
            for j in i:
                if p_nodes[j].data["status"] == "healthy":
                    h_n = j
                elif p_nodes[j].data["status"] == "infected":
                    i_n = j
            if h_n and i_n:
                hygiene = self._gethygiene(h_n, i_n)
                seed = p_nodes[h_n].seed["infection"]
                base_infection_chance = self._infection_chance(h_n, i_n)
                if seed < (base_infection_chance/hygiene):
                    p_nodes[h_n].infect()
                    status_count["infected"] += 1
                    status_count["healthy"] += -1

    def _update_status(self, overlaps, infected):
        self.status_count["serious without treatment"] = 0
        self.status_count["frames"] += 1
        self.status_count["days"] = int(self.status_count["frames"]/(WIN_FPS + 1))
        p_nodes = self.p_nodes
        for i in overlaps:
            for j in i:
                if j not in infected:
                    self._update_current_seed(p_nodes[j])
        for i in p_nodes:
            if i.data["status"] not in self.not_handle:
                self._update_current_seed(i)
                self._update_serious(i)
                self._update_treatment_status(i)
                self._update_immune(i)
        self._quarantine_nodes(infected)
        self._handle_dead(infected)
        self._handle_new_infections(overlaps)

    def _update_speed(self):
        for i in self.p_nodes:
            i.syncSpeed()
            #j["speed"] = i.data["speed"]

    def draw(self, dt, func, win):
        if not func.done:
            win.clear()
            infected, healthy = self._node_list("infected"), self._node_list("healthy")
            comp = infected, healthy
            overlaps = func.newframe(comp)
            self._update_speed()
            self._update_status(overlaps, infected)
            self.captured_data.append(dict(self.status_count))
            if STATUS_TEXT:
                self._status_draw()
            if self.status_count["infected"] == 0:
                self.done = True
                pyglet.app.exit()
                self._graph()
    
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

    def _graph(self):
        legend = {"dead" : DEAD_COLOR, "immune" : IMMUNE_COLOR, "healthy" : HEALTHY_COLOR, "infected" : INFECTED_COLOR, \
                  "serious in treatment" : IN_TREATMENT_COLOR, "serious without treatment" : SERIOUSLY_INFECTED_COLOR, 
                  "quarantined" : QUARANTINED_COLOR}
        Graph(self.captured_data, legend)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.done = True
            pyglet.app.exit()
            self._graph()
            #self._last_frame()

    def Start(self):
        w, h = self.win
        self.window = pyglet.window.Window(w, h, visible=False, caption=self.caption, vsync=0)
        self.window.set_visible()
        self.window.double_buffer = False
        self.nodes.data["resolution"] = NODE_RES
        self.window.on_mouse_press = self.on_mouse_press
        self._status_init()
        pyglet.clock.schedule_interval(self.draw, self.d_time, self.nodes, self.window)
        pyglet.app.run()
