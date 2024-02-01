
class Site:

    def __init__(self, pos, radius, regen_time, resource_count):
        self.REGEN_TIME = regen_time # the number of game ticks it takes for a site to completely regenerate resources
        self.MAX_RESOURCES = resource_count
        self.pos = pos
        self.radius = radius
        self.resource_count = resource_count
        self.timer = 0

    def update(self):
        if self.resource_count <= 0:
            if self.timer < self.REGEN_TIME:
                self.timer += 1
            else:
                self.resource_count = self.MAX_RESOURCES
                self.timer = 0

    def is_available(self):
        return self.resource_count != 0
