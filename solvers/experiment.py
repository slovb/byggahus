from enum import Enum
from tools.plan import Plan
from tools.newtonRaphson import find_root
import itertools

# Maintenance
HEALTH_THRESHOLD = {
    'EnvironmentalHouse': 41,
    'Other': 41
}

# Building
REQ_MAX_VACANCIES = 5
REQ_MIN_HOUSING_QUEUE = 14
MAX_RESIDENCES = 16
OPENER = [] # TODO
BUILDING_PRIORITY = ['LuxuryResidence', 'Cabin', 'HighRise', 'EnvironmentalHouse', 'ModernApartments', 'Apartments']
BASE_BUILD_PRIORITY = 4.0 # how many buildings are better than a utility, needs rethinking
MAX_BUILDINGS = {
    'LuxuryResidence': 1,
    'Cabin': 1,
    'HighRise': 1,
    'EnvironmentalHouse': 1,
    'ModernApartments': 11,
    'Apartments': 30
}

# Utilities
MAX_UTILITIES = {
    'Mall': 1,
    'Park': 2,
    'WindTurbine': 1
}

# Energy
DEG_PER_EXCESS_MWH = 0.75
DEG_PER_POP = 0.04

FORECAST_DAYS = 5
TEMP_TARGET = 21.0
TEMP_TOO_LOW = 19.5
TEMP_TOO_HIGH = 22.5
ENERGY_CHANGE_THRESHOLD = 1.0

DERIVATIVE_NUM_DAYS = 5
H = 0.01

class Urgency(Enum):
    NO = 0
    MINOR_ADJUST_ENERGY = 1
    CONSTRUCTION = 2
    UPGRADE = 3
    BUILD = 4
    MAJOR_ADJUST_ENERGY = 5
    MAINTENANCE = 6
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

memory = {}
def reset_memory():
    global memory
    memory = {
        'planned_buildings': [],
        'planned_utilities': [],
        'temperature': []
    }

def manhattan(u, v):
    return abs(v[0] - u[0]) + abs(v[1] - u[1])

def setup(game):
    reset_memory()
    state = game.game_state

    # if map square is occupied
    def is_occupied(position):
        if state.map[position[0]][position[1]] != 0:
            return True
        for residence in state.residences:
            if position == (residence.X, residence.Y):
                return True
        for utility in state.utilities:
            if position == (utility.X, utility.Y):
                return True
        return False

    # buildable spots, this assume square maps
    buildable_spots = list(filter(lambda p: not is_occupied(p), list(itertools.product(range(len(state.map)), range(len(state.map))))))
 
    # score area for building based on available utility effects
    def score(pos, planned_utilities):
        stuff = set()
        for utility in state.utilities:
            for name in game.get_blueprint(utility.building_name).effects:
                effect = game.get_effect(name)
                if manhattan(pos, (utility.X, utility.Y)) <= effect.radius:
                    stuff.add(effect.name)
        for utility_position, utility_name in planned_utilities:
            for effect_name in game.get_blueprint(utility_name).effects:
                if manhattan(pos, utility_position) <= game.get_effect(effect_name).radius:
                    stuff.add(effect_name)
        return len(stuff)
    
    # find all the sites for buildings with associated score
    def scored_buildable_positions(utilities):
        sites = {}
        for pos in buildable_spots:
            occupied = False
            for utility_position, _ in utilities:
                if pos == utility_position:
                    occupied = True
                    break
            if not occupied:
                for utility in state.utilities:
                    if pos == (utility.X, utility.Y):
                        occupied = True
                        break
            if not occupied:
                sites[pos] = score(pos, utilities)
        return sites

    # true if building is available on this map
    def building_is_available(building_name):
        for building in state.available_residence_buildings:
            if building_name == building.building_name:
                return True
        for building in state.available_utility_buildings:
            if building_name == building.building_name:
                return True
        return False

    def residences_to_build():
        return max(0, MAX_RESIDENCES - len(state.residences))

    # plan utilities
    def planned_utilities():
        # score the map for usable utilities
        def utility_score(utilities):
            sites = scored_buildable_positions(utilities)
            total = sum([v for k, v in sorted(sites.items(), key=lambda item: item[1], reverse=True)][:residences_to_build()])
            for residence in state.residences:
                total += score((residence.X, residence.Y), utilities)
            return total

        # try to add utility_name utility to the list of utilities
        def place(utility_name, utilities):
            occupied = [p for p, _ in utilities]
            # plan
            best_utilities = utilities
            best_score = utility_score(best_utilities)
            for pos in buildable_spots:
                if pos in occupied:
                    continue
                total = utility_score(utilities + [(pos, utility_name)])
                if total > best_score:
                    best_score = total
                    best_utilities = utilities + [(pos, utility_name)]
            return best_utilities

        # prepare to plan utilities
        utility_queue = []
        for building_name in filter(building_is_available, ['Mall', 'WindTurbine', 'Park']):
            # figure out how many utilities to plan
            count = MAX_UTILITIES[building_name] - len(list(filter(lambda b: building_name == b.building_name, state.utilities)))
            utility_queue += [building_name] * max(0, count)
        # plan utilities
        utilities = []
        for utility_name in utility_queue:
            utilities = place(utility_name, utilities)
        return utilities
    
    # get the best buildingsites in order
    def planned_buildings(utilities):
        sites = scored_buildable_positions(utilities)
        positions = [k for k, v in sorted(sites.items(), key=lambda item: item[1], reverse=True)][:residences_to_build()]
        build_queue = []
        for building_name in filter(building_is_available, BUILDING_PRIORITY):
            # figure out how many buildings to plan
            count = MAX_BUILDINGS[building_name] - len(list(filter(lambda b: building_name == b.building_name, state.residences)))
            build_queue += [building_name] * max(0, count)
        build_queue = build_queue[:len(positions)]
        return list(zip(positions, build_queue))

    utilities = planned_utilities()
    memory['planned_utilities'] = utilities
    memory['planned_buildings'] = planned_buildings(utilities)
    

def take_turn(game):
    memory['temperature'].append(game.game_state.current_temp)
    plans = [Plan(Urgency.NO, 0.0).wait()] + find_build(game) + find_construction(game) + find_utilities(game) + find_upgrades(game) + find_maintenance(game) + find_adjust_energy(game)
    max(plans).do(game)

def find_build(game):
    state = game.game_state
    # always continue construction
    plans = []
    for residence in state.residences:
        if residence.build_progress < 100:
            plans.append(Plan(Urgency.BUILD, 0.0).build((residence.X, residence.Y)))
    return plans

def available_buildings(state):
    output = []
    for b in state.available_residence_buildings:
        if state.turn > b.release_tick:
            output.append(b.building_name)
    return output

def find_construction(game):
    state = game.game_state
    plans = []
    # new construction?
    available = available_buildings(state)
    vacancies = sum([game.get_blueprint(residence.building_name).max_pop - residence.current_pop for residence in state.residences])
    bad_time = state.housing_queue < REQ_MIN_HOUSING_QUEUE or vacancies > REQ_MAX_VACANCIES
    priority = 1
    for entry in memory['planned_buildings']:
        position, building_name = entry
        if building_name not in available:
            continue
        bp = game.get_blueprint(building_name)
        score = BASE_BUILD_PRIORITY - 0.01*priority
        plan = Plan(Urgency.CONSTRUCTION, score).construction(position, building_name).forget_entry(memory, 'planned_buildings', entry)
        if bad_time or state.funds < bp.cost:
            plan = Plan(Urgency.CONSTRUCTION, score).wait()
        plans.append(plan)
        priority += 1
    return plans

def find_utilities(game):
    state = game.game_state
    def score(pos, bp):
        val = 0
        for residence in state.residences:
            for effect_name in bp.effects:
                effect = game.get_effect(effect_name)
                if manhattan(pos, (residence.X, residence.Y)) <= effect.radius:
                    val += 1
        return val
    plans = []
    for entry in memory['planned_utilities']:
        position, building_name = entry
        bp = game.get_blueprint(building_name)
        if (state.funds >= bp.cost) and state.turn >= bp.release_tick:
            plans.append(Plan(Urgency.CONSTRUCTION, score(position, bp)).construction(position, building_name).forget_entry(memory, 'planned_utilities', entry))
    return plans

def find_upgrades(game):
    state = game.game_state
    plans = []
    upgrades = {}
    if state.funds > 30000:
        upgrades = {
            'Apartments': ['SolarPanel', 'Playground', 'Caretaker'],
            'ModernApartments': ['SolarPanel', 'Playground', 'Caretaker'],
            'EnvironmentalHouse': ['Insulation'],
            'HighRise': ['Caretaker', 'Playground']
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
        threshold = HEALTH_THRESHOLD['Other']
        if residence.building_name in HEALTH_THRESHOLD:
            threshold = HEALTH_THRESHOLD[residence.building_name]
        if residence.health < threshold:
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
        emissivity = bp.emissivity
        for name in residence.effects:
            if name == 'Insulation':
                emissivity *= 0.6
        def indoor_temp_forecast(energy_in):
            temp = residence.temperature
            o_dt = temperatureDerivative()
            for i in range(FORECAST_DAYS):
                o_at_t = outside_temp + (i + 1) * o_dt
                temp = new_temp(energy_in, bp.base_energy_need, temp, o_at_t, residence.current_pop, emissivity)
            return temp
        f = lambda energy_in: TEMP_TARGET - indoor_temp_forecast(energy_in)
        energy = find_root(f, residence.effective_energy_in, H)
        return max(bp.base_energy_need, energy)
    state = game.game_state
    plans = []
    for residence in state.residences:
        need = get_energy_need(residence, state.current_temp)
        urgency = Urgency.MINOR_ADJUST_ENERGY
        if residence.temperature < TEMP_TOO_LOW or residence.temperature > TEMP_TOO_HIGH:
            urgency = Urgency.MAJOR_ADJUST_ENERGY        
        change = abs(need - residence.requested_energy_in)
        score = change * residence.current_pop
        if change > ENERGY_CHANGE_THRESHOLD:
            plans.append(Plan(urgency, score).adjustEnergy((residence.X, residence.Y), need))
    return plans
