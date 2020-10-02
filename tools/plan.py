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
        self.name = 'wait'
        self.plan = lambda game: game.wait()
        return self
    def build(self, pos):
        self.name = 'build'
        self.plan = lambda game: game.build(pos)
        return self
    def construction(self, pos, building_name):
        self.name = 'constru'
        self.plan = lambda game: game.place_foundation(pos, building_name)
        return self
    def upgrade(self, pos, name):
        self.name = 'upgrade'
        self.plan = lambda game: game.buy_upgrade(pos, name)
        return self
    def maintenance(self, pos):
        self.name = 'mainten'
        self.plan = lambda game: game.maintenance(pos)
        return self
    def adjust_energy(self, pos, energy):
        self.name = 'energy'
        def plan(game):
            print(energy)
            game.adjust_energy_level(pos, energy)
        self.plan = plan
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
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            if self.urgency > other.urgency:
                return True
            elif self.urgency == other.urgency:
                return self.score > other.score
            return False
        return NotImplemented
