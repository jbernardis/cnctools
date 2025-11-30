import math

class Rotator:
    def __init__(self, angle):
        self.cosv = math.cos(math.radians(angle))
        self.sinv = math.sin(math.radians(angle))
        
    def rotate(self, x, y):        
        return x*self.cosv-y*self.sinv, x*self.sinv+y*self.cosv

