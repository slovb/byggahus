from enum import Enum
from tools.plan import Plan

DEG_PER_EXCESS_MWH = 0.75
DEG_PER_POP = 0.04

class Urgency(Enum):
    NO = 0
    MINOR_ADJUST_ENERGY = 1
    MAJOR_ADJUST_ENERGY = 2
    CONSTRUCTION = 3
    UPGRADE = 4
    BUILD = 5
    MAINTENANCE = 6
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

memory = {}

def take_turn(game):
    plans = [Plan(Urgency.NO, 0.0).wait()] + find_build(game) + find_construction(game) + find_upgrades(game) + find_maintenance(game) + find_adjust_energy(game)
    max(plans).do(game)

def find_build(game):
    state = game.game_state
    # always continue construction
    plans = []
    for residence in state.residences:
        if residence.build_progress < 100:
            plans.append(Plan(Urgency.BUILD, 0.0).build((residence.X, residence.Y)))
    return plans

def find_construction(game):
    state = game.game_state
    plans = []
    # new construction?
    building_name = "Apartments"
    pop_tot = 0
    pop_cap = 0
    for residence in state.residences:
        pop_tot += residence.current_pop
        pop_cap += game.get_blueprint(building_name).max_pop
    if (state.funds >= game.get_blueprint(building_name).cost and 
        state.housing_queue >= 14 and
        pop_cap - pop_tot <= 5):
        for i in range(len(state.map)):
            for j in range(len(state.map)):
                if state.map[i][j] == 0:
                    plotTaken = False
                    for residence in state.residences:
                        if residence.X == i and residence.Y == j:
                            plotTaken = True
                            break
                    if not plotTaken:
                        x = i
                        y = j
                        plans.append(Plan(Urgency.CONSTRUCTION, 0.0).construction((x, y), building_name))
    return plans

def find_upgrades(game):
    global memory
    state = game.game_state
    plans = []
    upgrades = ["Caretaker", "SolarPanel"]
    #if state.turn > 600:
    #    upgrades.append("Playground")
    #if state.turn > 400 and regulator_count < 7:
    #    upgrades.append("Insulator")
    for residence in state.residences:
        for priority, name in enumerate(upgrades):
            upgrade = next((upgrade for upgrade in state.available_upgrades if upgrade.name == name), None)
            if upgrade is not None and name not in residence.effects and state.funds >= upgrade.cost:
                score = 10.0 - priority
                plans.append(Plan(Urgency.UPGRADE, score).upgrade((residence.X, residence.Y), name).remember_count(memory, 'upgrade', name))
    return plans

def find_maintenance(game):
    state = game.game_state
    HEALTH_THRESHOLD = 40
    plans = []
    for residence in state.residences:
        if residence.health < HEALTH_THRESHOLD:
            plans.append(Plan(Urgency.MAINTENANCE, 100.0 - residence.health).maintenance((residence.X, residence.Y)))
    return plans

def find_adjust_energy(game):
    state = game.game_state
    def get_energy_need(residence, outsideTemp):
        DAYS_TO_FIXED = 5.0
        TARGET_TEMP = 21.0
        bp = game.get_residence_blueprint(residence.building_name)
        current_energy_need = bp.base_energy_need + (TARGET_TEMP - residence.temperature - DEG_PER_POP * residence.current_pop + (residence.temperature - outsideTemp) * bp.emissivity)/DEG_PER_EXCESS_MWH
        return max(bp.base_energy_need, bp.base_energy_need + (current_energy_need - bp.base_energy_need) / DAYS_TO_FIXED)
    plans = []
    for residence in state.residences:
        need = get_energy_need(residence, state.current_temp)
        urgency = Urgency.MINOR_ADJUST_ENERGY
        if residence.temperature < 19.5 or residence.temperature > 22.5:
            urgency = Urgency.MAJOR_ADJUST_ENERGY        
        score = abs(need - residence.requested_energy_in)
        plans.append(Plan(urgency, score).adjustEnergy((residence.X, residence.Y), need))
    return plans