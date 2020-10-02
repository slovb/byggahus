from enum import Enum
from tools.plan import Plan
from tools.newtonRaphson import find_root, dfdx
import itertools

class Settings():
    class Maintenance():
        def __init__(self):
            self.THRESHOLD = {
                'EnvironmentalHouse': 41,
                'Other': 41
            }

    class Building():
        def __init__(self):
            self.REQ_MAX_VACANCIES = 5
            self.REQ_MIN_HOUSING_QUEUE = 14
            self.LIMIT_RESIDENCES = 17
            self.PRIORITY = ['LuxuryResidence', 'HighRise', 'Apartments', 'Cabin', 'EnvironmentalHouse', 'ModernApartments']
            self.PRIORITY_VALUE = 4.0 # how many buildings are better than a utility, needs rethinking
            self.LIMIT = {
                'Apartments': 1,
                'Cabin': 1,
                'EnvironmentalHouse': 1,
                'HighRise': 1,
                'LuxuryResidence': 1,
                'ModernApartments': 9
            }
            self.FILL = ['Apartments']
            self.DELAY = {
                'HighRise': 100
            }

    class Upgrade():
        def __init__(self):
            self.FUNDS_THRESHOLD = 22000
            self.PRIORITY = {
                'Apartments': ['SolarPanel', 'Insulation', 'Caretaker', 'Playground', 'Charger'],
                'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Caretaker', 'Charger'],
                'EnvironmentalHouse': ['SolarPanel', 'Insulation', 'Caretaker'],
                'LuxuryResidence': ['SolarPanel', 'Caretaker', 'Regulator', 'Playground'],
                'Cabin': [],
                'HighRise': ['Playground', 'Charger', 'Caretaker', 'Insulation']
            }

    class Utility():
        def __init__(self):
            self.LIMIT = {
                'Mall': 1,
                'Park': 1,
                'WindTurbine': 1
            }

    class Energy():
        def __init__(self):
            self.DEG_PER_EXCESS_MWH = 0.75
            self.DEG_PER_POP = 0.04
            self.FORECAST_DAYS = 15
            self.TEMP_TARGET = 21.0
            self.TEMP_TOO_LOW = 18.5
            self.TEMP_TOO_HIGH = 23.5
            self.THRESHOLD = 0.001

    class Math():
        def __init__(self):
            self.DERIVATIVE_NUM_DAYS = 5
            self.H = 0.001

    def __init__(self):
        self.MAINTENANCE = self.Maintenance()
        self.BUILDING = self.Building()
        self.UPGRADE = self.Upgrade()
        self.UTILITY = self.Utility()
        self.ENERGY = self.Energy()
        self.MATH = self.Math()

class Urgency(Enum):
    NOP = 0
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

SETTINGS = Settings()
memory = {}
def reset_memory():
    global memory
    memory = {
        'planned_buildings': [],
        'planned_utilities': [],
        'temperature': [],
        'urgencies': {}
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
        return max(0, SETTINGS.BUILDING.LIMIT_RESIDENCES - len(state.residences))

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
            count = SETTINGS.UTILITY.LIMIT[building_name] - len(list(filter(lambda b: building_name == b.building_name, state.utilities)))
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
        for building_name in filter(building_is_available, SETTINGS.BUILDING.PRIORITY):
            # figure out how many buildings to plan
            count = SETTINGS.BUILDING.LIMIT[building_name] - len(list(filter(lambda b: building_name == b.building_name, state.residences)))
            build_queue += [building_name] * max(0, count)
        # fill up with extra buildings if limits were too strict
        if len(build_queue) < len(positions):
            available_fill = list(filter(building_is_available, SETTINGS.BUILDING.FILL))
            build_queue += [available_fill[0]] * (len(positions) - len(build_queue))
        build_queue = build_queue[:len(positions)]
        return list(zip(positions, build_queue))

    utilities = planned_utilities()
    memory['planned_utilities'] = utilities
    memory['planned_buildings'] = planned_buildings(utilities)


def take_turn(game):
    memory['temperature'].append(game.game_state.current_temp)
    plans = [Plan(Urgency.NOP, 0.0).wait()] + find_build(game) + find_construction(game) + find_utilities(game) + find_upgrades(game) + find_maintenance(game) + find_adjust_energy(game)
    plan = max(plans)
    plan = plan.remember_count(memory, 'urgencies', (plan.name, plan.urgency))
    plan.do(game)
    return memory['urgencies']

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
            if b.building_name not in SETTINGS.BUILDING.DELAY or state.turn > SETTINGS.BUILDING.DELAY[b.building_name]:
                output.append(b.building_name)
    return output

def find_construction(game):
    state = game.game_state
    plans = []
    # new construction?
    available = available_buildings(state)
    vacancies = sum([game.get_blueprint(residence.building_name).max_pop - residence.current_pop for residence in state.residences])
    bad_time = state.housing_queue < SETTINGS.BUILDING.REQ_MIN_HOUSING_QUEUE or vacancies > SETTINGS.BUILDING.REQ_MAX_VACANCIES
    priority = 1
    for entry in memory['planned_buildings']:
        position, building_name = entry
        if building_name not in available:
            continue
        bp = game.get_blueprint(building_name)
        score = SETTINGS.BUILDING.PRIORITY_VALUE - 0.01*priority
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
    COST = { # todo get
        'Caretaker': 3500,
        'SolarPanel': 6800,
        'Insulation': 7200,
        'Playground': 5200,
        'Charger': 3400,
        'Regulator': 1250
    }
    if state.funds > SETTINGS.UPGRADE.FUNDS_THRESHOLD:
        upgrades = SETTINGS.UPGRADE.PRIORITY
    for residence in state.residences:
        if residence.building_name in upgrades:
            for priority, upgrade_name in enumerate(upgrades[residence.building_name]):
                if upgrade_name not in residence.effects:
                    score = 10.0 - priority
                    plan = Plan(Urgency.UPGRADE, score).upgrade((residence.X, residence.Y), upgrade_name).remember_count(memory, 'upgrade', upgrade_name)
                    if state.funds < COST[upgrade_name]: # never will happen with high threshold
                        plan = Plan(Urgency.UPGRADE, score).wait()
                    plans.append(plan)
    return plans

def find_maintenance(game):
    state = game.game_state
    plans = []
    COST = {
        'Apartments': 950,
        'ModernApartments': 1050,
        'Cabin': 450,
        'EnvironmentalHouse': 950,
        'HighRise': 2770,
        'LuxuryResidence': 950
    }
    for residence in state.residences:
        threshold = SETTINGS.MAINTENANCE.THRESHOLD['Other']
        if residence.building_name in SETTINGS.MAINTENANCE.THRESHOLD:
            threshold = SETTINGS.MAINTENANCE.THRESHOLD[residence.building_name]
        score = 100.0 - residence.health
        if residence.health < threshold:
            plan = Plan(Urgency.MAINTENANCE, score).maintenance((residence.X, residence.Y))
            if state.funds < COST[residence.building_name]:
                plan = Plan(Urgency.MAINTENANCE, score).wait()
            plans.append(plan)
    return plans

def temperature_derivative():
    t = memory["temperature"]
    if len(t) == 0 or len(t) == 1:
        return 0.0
    elif len(t) < SETTINGS.MATH.DERIVATIVE_NUM_DAYS:
        return (t[-1] - t[0]) / (len(t) - 1)
    return (t[-1] - t[-SETTINGS.MATH.DERIVATIVE_NUM_DAYS]) / (SETTINGS.MATH.DERIVATIVE_NUM_DAYS - 1)

def estimate_outdoor_temperature_in_days(state, i, outside_temp):
    LENGTH_OF_YEAR = 183
    if state.turn > LENGTH_OF_YEAR:
        return memory['temperature'][(state.turn + i) % LENGTH_OF_YEAR]
    return outside_temp + i * temperature_derivative()

def new_temp(energy_in, base_energy, indoor_temperature, outdoor_temperature, current_pop, emissivity):
    return indoor_temperature + (energy_in - base_energy) * SETTINGS.ENERGY.DEG_PER_EXCESS_MWH + SETTINGS.ENERGY.DEG_PER_POP * current_pop - (indoor_temperature - outdoor_temperature) * emissivity

def find_adjust_energy(game):
    ENERGY_CHANGE_COST = 150
    INSULATION_EMISSIVITY_MODIFIER = 0.6
    CHARGER_BASE_ENERGY_INCREASE = 1.8
    GOOD_MODIFIER = 0.1
    state = game.game_state
    def get_energy_need(residence):
        outside_temp = state.current_temp
        bp = game.get_residence_blueprint(residence.building_name)
        base_energy = bp.base_energy_need
        emissivity = bp.emissivity
        for name in residence.effects:
            if name == 'Insulation':
                emissivity *= INSULATION_EMISSIVITY_MODIFIER
            elif name == 'Charger':
                base_energy += CHARGER_BASE_ENERGY_INCREASE
        # the amount of degrees off target through the period
        def score(energy_in):
            def val(temp):
                if temp < SETTINGS.ENERGY.TEMP_TOO_LOW:
                    return abs(SETTINGS.ENERGY.TEMP_TOO_LOW - temp) + GOOD_MODIFIER * (SETTINGS.ENERGY.TEMP_TARGET - SETTINGS.ENERGY.TEMP_TOO_LOW)
                elif temp > SETTINGS.ENERGY.TEMP_TOO_HIGH:
                    return abs(SETTINGS.ENERGY.TEMP_TOO_HIGH - temp) + GOOD_MODIFIER * (SETTINGS.ENERGY.TEMP_TOO_HIGH - SETTINGS.ENERGY.TEMP_TARGET)
                return GOOD_MODIFIER * abs(SETTINGS.ENERGY.TEMP_TARGET - temp)
            total = 0.0
            temp = residence.temperature
            for i in range(SETTINGS.ENERGY.FORECAST_DAYS):
                outsideEstimate = estimate_outdoor_temperature_in_days(state, i, outside_temp)
                temp = new_temp(energy_in, base_energy, temp, outsideEstimate, residence.current_pop, emissivity)
                total += val(temp)
            return total
        def guess():
            return base_energy + (SETTINGS.ENERGY.TEMP_TARGET - residence.temperature + SETTINGS.ENERGY.DEG_PER_POP * residence.current_pop + (residence.temperature - outside_temp) * emissivity) / SETTINGS.ENERGY.DEG_PER_EXCESS_MWH
        # trying to minimize a strictly positive function, so take the derivative
        f = lambda energy_in: dfdx(score, energy_in, SETTINGS.MATH.H)
        guess = guess() - 5.0*SETTINGS.MATH.H
        energy = find_root(score, guess, SETTINGS.MATH.H)
        return max(base_energy, energy)
    plans = []
    for residence in state.residences:
        need = get_energy_need(residence)
        urgency = Urgency.MINOR_ADJUST_ENERGY
        if residence.temperature < SETTINGS.ENERGY.TEMP_TOO_LOW or residence.temperature > SETTINGS.ENERGY.TEMP_TOO_HIGH:
            urgency = Urgency.MAJOR_ADJUST_ENERGY
        change = abs(need - residence.requested_energy_in)
        score = change * residence.current_pop
        if change > SETTINGS.ENERGY.THRESHOLD:
            plan = Plan(urgency, score).adjust_energy((residence.X, residence.Y), need)
            if state.funds < ENERGY_CHANGE_COST:
                plan = Plan(urgency, score).wait()
            plans.append(plan)
    return plans

