#PandemicNode.py
import random
import math
from Pandemic_config import *

class PandemicNode:
    
    node_spec = {"healthy" : {"color" : HEALTHY_COLOR, "speed" : HEALTHY_SPEED, "radius" : HEALTHY_RADIUS},
                 "infected" : {"color" : INFECTED_COLOR, "speed" : INFECTED_SPEED, "radius" : INFECTED_RADIUS},
                 "immune" : {"color" : IMMUNE_COLOR, "speed" : IMMUNE_SPEED, "radius" : IMMUNE_RADIUS}, 
                 "dead" : {"color" : DEAD_COLOR, "speed" : DEAD_SPEED, "radius" : DEAD_RADIUS},
                 "quarantined" : {"color" : QUARANTINED_COLOR, "speed" : QUARANTINED_SPEED, "radius" : QUARANTINED_RADIUS}}

    def __init__(self, status, nodegroup, w, h):
        angle = random.random()*2*math.pi
        h_speed = self.node_spec[status]["speed"]
        i_speed = (h_speed[1] - h_speed[0])*random.random()
        i_speed += h_speed[0]
        xs, ys = math.cos(angle)*i_speed, math.sin(angle)*i_speed
        color = self.node_spec[status]["color"]
        pos = [random.randint(0, w), random.randint(0, h)]
        speed = (xs, ys)
        radius = self.node_spec[status]["radius"]
        node_number = nodegroup.AddNode(speed, color, radius, pos)
        risk_group = True
        self.seed = {"infection" : 0, "serious" : 0, "quarantined" : 0, "dead" : 0}
        if random.random() > RISK_GROUP_PORTION:
            risk_group = False
        self.data ={"status" : status, "days sick" : 0, "risk group" : risk_group, 
                    "serious" : False, "in treatment" : False, "days in treatment" : 0,
                    "current seed" : 0, "speed" : (xs, ys), "self isolated" : False,
                    "practicing hygiene" : False, "quarantined" : False, 
                    "node number" : node_number, "node group" : nodegroup}
    

    def _updateSpeed(self, speed = None):
        n = self.data["node number"]
        status = self.data["status"]
        if self.node_spec[status]["speed"] == [0, 0]:
            self.data["node group"].nodes[n].data["speed"] = self.node_spec[status]["speed"]
        else:
            angle = random.random()*2*math.pi
            h_speed = self.node_spec[status]["speed"]
            i_speed = (h_speed[1] - h_speed[0])*random.random()
            i_speed += h_speed[0]
            xs, ys = math.cos(angle)*i_speed, math.sin(angle)*i_speed
            if speed:
                xs, ys = speed
            self.data["node group"].nodes[n].data["speed"] = xs, ys
            self.data["speed"] = xs, ys

    def updateSpeed(self, speed):
        n = self.data["node number"]
        status = self.data["status"]
        if self.node_spec[status]["speed"] == [0, 0]:
            self.data["node group"].nodes[n].data["speed"] = self.node_spec[status]["speed"]
        else:
            angle = random.random()*2*math.pi
            h_speed = speed
            i_speed = (h_speed[1] - h_speed[0])*random.random()
            i_speed += h_speed[0]
            xs, ys = math.cos(angle)*i_speed, math.sin(angle)*i_speed
            self.data["node group"].nodes[n].data["speed"] = xs, ys
            self.data["speed"] = xs, ys

    def updateStatus(self, status):
        n = self.data["node number"]
        self.data["status"] = status
        self.data["node group"].nodes[n].data["color"] = self.node_spec[status]["color"]
        self._updateSpeed()
    
    def Serious(self):
        n = self.data["node number"]
        self.data["serious"] = True
        self.data["node group"].nodes[n].data["color"] = SERIOUSLY_INFECTED_COLOR
        self._updateSpeed(SERIOUS_SPEED)
    
    def inTreatment(self, quarantine_in_treatment):
        n = self.data["node number"]
        self.data["in treatment"] = True
        if quarantine_in_treatment:
            self.data["quarantined"] = True
        self.data["node group"].nodes[n].data["color"] = IN_TREATMENT_COLOR
        self._updateSpeed(IN_TREATMENT_SPEED)
    
    def treatmentOver(self, immune, keepquarantine = True):
        n = self.data["node number"]
        self.data["in treatment"] = False
        self.data["serious"] = False
        quarantined = self.data["quarantined"]
        if immune:
            self.updateStatus("immune")
            self.data["quarantined"] = False
        elif quarantined and keepquarantine:
            self.quarantined()
        else:
            self.data["node group"].nodes[n].data["color"] = INFECTED_COLOR
            self.updateStatus("infected")
            #self.data["status"] = "infected"
            #self.updateSpeed(INFECTED_SPEED)
    
    def infect(self):
        n = self.data["node number"]
        self.data["status"] = "infected"
        self.data["node group"].nodes[n].data["color"] = INFECTED_COLOR
        factor = INFECTED_SPEED[1]/HEALTHY_SPEED[1]
        xs, ys = self.data["speed"][0]*factor, self.data["speed"][1]*factor
        self._updateSpeed((xs, ys))
    
    def immune(self):
        n = self.data["node number"]
        self.data["status"] = "immune"
        self.data["in treatment"] = False
        self.data["Serious"] = False
        self.data["quarantined"] = False
        self.data["node group"].nodes[n].data["color"] = IMMUNE_COLOR
        self._updateSpeed(IMMUNE_SPEED)
    
    def quarantined(self):
        n = self.data["node number"]
        self.data["quarantined"] = True
        self.data["node group"].nodes[n].data["color"] = QUARANTINED_COLOR
        self._updateSpeed(QUARANTINED_SPEED)
    
    def kill(self):
        n = self.data["node number"]
        self.data["status"] = "dead"
        status = "dead"
        self.data["quarantined"] = False
        self.data["serious"] = False
        self.data["in treatment"] = False
        self.data["self isolated"] = False
        self.data["node group"].nodes[n].data["color"] = self.node_spec[status]["color"]
        self._updateSpeed()

    def reSeed(self):
        for i in self.seed:
            self.seed[i] = random.random()
    
    def syncSpeed(self):
        n = self.data["node number"]
        self.data["speed"] = self.data["node group"].nodes[n].data["speed"]

    def syncGraphSpeed(self):
        n = self.data["node number"]
        self.data["node group"].nodes[n].data["speed"] = self.data["speed"]