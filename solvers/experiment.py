from enum import Enum
from tools.plan import Plan
from tools.newtonRaphson import find_root

# Maintenance
HEALTH_THRESHOLD = 41

# Energy
DEG_PER_EXCESS_MWH = 0.75
DEG_PER_POP = 0.04

FORECAST_DAYS = 10
TEMP_TARGET = 21.0
TEMP_LOW = 19.5
TEMP_HIGH = 22.5
ENERGY_CHANGE_THRESHOLD = 1.0

DERIVATIVE_NUM_DAYS = 5
H = 0.01

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

memory = {
    'temperature': [],
    'viable_build_sites': []
}

def setup(game):
    state = game.game_state
    for i in range(len(state.map)):
        for j in range(len(state.map)):
            if state.map[i][j] == 0:
                memory['viable_build_sites'].append((i, j))

def take_turn(game):
    memory['temperature'].append(game.game_state.current_temp)
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

def viable_buildings(state):
    output = []
    for b in state.available_residence_buildings:
        if state.turn > b.release_tick:
            output.append(b.building_name)
    return output

def find_construction(game):
    state = game.game_state
    plans = []
    # new construction?
    buildings = ["HighRise", "EnvironmentalHouse", "ModernApartments", "Apartments"]
    viable = viable_buildings(state)
    for priority, building_name in enumerate(buildings):
        if building_name not in viable:
            continue
        for pos in memory["viable_build_sites"]:
            pop_tot = 0
            pop_cap = 0
            for residence in state.residences:
                pop_tot += residence.current_pop
                pop_cap += game.get_blueprint(building_name).max_pop
            if (state.funds >= game.get_blueprint(building_name).cost and 
                state.housing_queue >= 14 and
                pop_cap - pop_tot <= 5):
                plans.append(Plan(Urgency.CONSTRUCTION, 10.0 - priority).construction(pos, building_name).forget_entry(memory, 'viable_build_sites', pos))
    return plans

def find_upgrades(game):
    state = game.game_state
    plans = []
    upgrades = {}
    if state.funds > 30000:
        upgrades = {
            "Apartments": ["Playground", "SolarPanel", "Caretaker"],
            "ModernApartments": ["Playground", "SolarPanel", "Caretaker"],
            "EnvironmentalHouse": [],
            "HighRise": ["Caretaker", "Playground"]
        }
    for residence in state.residences:
        if residence.building_name in upgrades:
            for priority, name in enumerate(upgrades[residence.building_name]):
                upgrade = next((upgrade for upgrade in state.available_upgrades if upgrade.name == name), None)
                if upgrade is not None and name not in residence.effects and state.funds >= upgrade.cost:
                    score = 10.0 - priority
                    plans.append(Plan(Urgency.UPGRADE, score).upgrade((residence.X, residence.Y), name).remember_count(memory, 'upgrade', name))
    return plans

def find_maintenance(game):
    state = game.game_state
    plans = []
    for residence in state.residences:
        if residence.health < HEALTH_THRESHOLD:
            plans.append(Plan(Urgency.MAINTENANCE, 100.0 - residence.health).maintenance((residence.X, residence.Y)))
    return plans

def temperatureDerivative():
    t = memory["temperature"]
    if len(t) == 0 or len(t) == 1:
        return 0.0
    elif len(t) < DERIVATIVE_NUM_DAYS:
        return (t[-1] - t[0]) / (len(t) - 1)
    return (t[-1] - t[-DERIVATIVE_NUM_DAYS]) / (DERIVATIVE_NUM_DAYS - 1)

def new_temp(energy_in, base_energy, indoor_temperature, outdoor_temperature, current_pop, emissivity):
    return indoor_temperature + (energy_in - base_energy) * DEG_PER_EXCESS_MWH + DEG_PER_POP * current_pop - (indoor_temperature - outdoor_temperature) * emissivity

def find_adjust_energy(game):
    def get_energy_need(residence, outside_temp):
        bp = game.get_residence_blueprint(residence.building_name)
        def indoor_temp_forecast(energy_in):
            temp = residence.temperature
            o_dt = temperatureDerivative()
            for i in range(FORECAST_DAYS):
                o_at_t = outside_temp + (i + 1) * o_dt
                temp = new_temp(energy_in, bp.base_energy_need, temp, o_at_t, residence.current_pop, bp.emissivity)
            return temp
        f = lambda energy_in: TEMP_TARGET - indoor_temp_forecast(energy_in)
        energy = find_root(f, residence.effective_energy_in, H)
        return max(bp.base_energy_need, energy)
    state = game.game_state
    plans = []
    for residence in state.residences:
        need = get_energy_need(residence, state.current_temp)
        urgency = Urgency.MINOR_ADJUST_ENERGY
        if residence.temperature < TEMP_LOW or residence.temperature > TEMP_HIGH:
            urgency = Urgency.MAJOR_ADJUST_ENERGY        
        change = abs(need - residence.requested_energy_in)
        score = change * residence.current_pop
        if change > ENERGY_CHANGE_THRESHOLD:
            plans.append(Plan(urgency, score).adjustEnergy((residence.X, residence.Y), need))
    return plans