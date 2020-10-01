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
    def remember_count(self, memory, key, entry):
        def after():
            if key not in memory:
                memory[key] = {}
            if entry not in memory[key]:
                memory[key][entry] = 0
            memory[key][entry] += 1
        self.after.append(after)
        return self
    def forget_entry(self, memory, key, entry):
        def after():
            memory[key].remove(entry)
        self.after.append(after)
        return self
    def forget_sub_entry(self, memory, key, sub_key, entry):
        def after():
            memory[key][sub_key].remove(entry)
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