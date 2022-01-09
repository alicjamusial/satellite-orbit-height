from math import pi

earth_radius = 6371


class Satellite:
    def __init__(self, satellite):
        self.epoch = satellite.epoch

        self.PeA = satellite.altp * earth_radius
        self.ApA = satellite.alta * earth_radius

        self.mean_height = (self.PeA + self.ApA) / 2
