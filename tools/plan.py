class Plan():
    def __init__(self, urgency, score):
        self.urgency = urgency
        self.score = score
        self.after = []
    def do(self, game):
        self.plan(game)
        for after in self.after:
            after()
        return self
    def wait(self):
        self.plan = lambda game: game.wait()
        return self
    def build(self, pos):
        self.plan = lambda game: game.build(pos)
        return self
    def construction(self, pos, building_name):
        self.plan = lambda game: game.place_foundation(pos, building_name)
        return self
    def upgrade(self, pos, name):
        self.plan = lambda game: game.buy_upgrade(pos, name)
        return self
    def maintenance(self, pos):
        self.plan = lambda game: game.maintenance(pos)
        return self
    def adjustEnergy(self, pos, energy):
        self.plan = lambda game: game.adjust_energy_level(pos, energy)
        return self
    def remember_count(self, memory, kind, key):
        def after():
            if kind not in memory:
                memory[kind] = {}
            if key not in memory[kind]:
                memory[kind][key] = 0
            memory[kind][key] += 1
        self.after.append(after)
        return self
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            if self.urgency > other.urgency:
                return True
            elif self.urgency == other.urgency:
                return self.score > other.score
            return False
        return NotImplemented