from enum import Enum
from tools.plan import Plan
from tools.dirtyEnergy import memorize_temperature, reset_temperature_memory, recommend_energy_adjustments, ENERGY
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
            self.FUNDS_THRESHOLD = 23000
            self.PRIORITY = {
                'Apartments': ['SolarPanel', 'Regulator', 'Insulation', 'Caretaker', 'Playground', 'Charger'],
                'ModernApartments': ['Regulator', 'Charger', 'Playground', 'SolarPanel', 'Caretaker', 'Insulation'],
                'EnvironmentalHouse': ['Regulator', 'Charger', 'SolarPanel', 'Insulation', 'Caretaker'],
                'LuxuryResidence': ['SolarPanel', 'Regulator', 'Caretaker', 'Regulator', 'Playground'],
                'Cabin': [],
                'HighRise': ['Playground', 'Regulator', 'Charger', 'Caretaker', 'Insulation']
            }
            self.CHARGER_ONLY_ON_MALL = True
            self.WAIT_FOR_UPGRADE = True

    class Utility():
        def __init__(self):
            self.LIMIT = {
                'Mall': 1,
                'Park': 2,
                'WindTurbine': 1
            }
            self.THRESHOLD = 3

    class Math():
        def __init__(self):
            self.DERIVATIVE_NUM_DAYS = 5
            self.H = 0.001

    def __init__(self):
        self.MAINTENANCE = self.Maintenance()
        self.BUILDING = self.Building()
        self.UPGRADE = self.Upgrade()
        self.UTILITY = self.Utility()
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
        'urgencies': {}
    }

def manhattan(u, v):
    return abs(v[0] - u[0]) + abs(v[1] - u[1])

def setup(game):
    reset_memory()
    reset_temperature_memory()
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
    memorize_temperature(game.game_state.current_temp)
    plans = [Plan(Urgency.NOP, 0.0).wait()] + find_build(game) + find_construction(game) + find_utilities(game) + find_upgrades(game) + find_maintenance(game) + find_adjust_energy(game)
    plan = max(plans)
    plan = plan.remember_count(memory, 'urgencies', (plan.name, plan.urgency))
    print(' ')
    print(plan)
    plan.do(game)
    return memory['urgencies']

def find_build(game):
    state = game.game_state
    # always continue construction
    plans = []
    for residence in state.residences:
        if residence.build_progress < 100:
            plans.append(Plan(Urgency.BUILD, residence.build_progress).build((residence.X, residence.Y)))
    for utility in state.utilities:
        if utility.build_progress < 100:
            plans.append(Plan(Urgency.BUILD, utility.build_progress).build((utility.X, utility.Y)))
    return plans

def available_buildings(state):
    output = []
    for b in state.available_residence_buildings:
        if state.turn >= b.release_tick:
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
        priority += 1
        plan = Plan(Urgency.CONSTRUCTION, score)
        if bad_time:
            pass
        elif state.funds < bp.cost:
            plans.append(plan.wait())
        else:
            plans.append(plan.construction(position, building_name).forget_entry(memory, 'planned_buildings', entry))     
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
            val = score(position, bp)
            if val >= SETTINGS.UTILITY.THRESHOLD:
                plans.append(Plan(Urgency.CONSTRUCTION, score(position, bp)).construction(position, building_name).forget_entry(memory, 'planned_utilities', entry))
    return plans

def find_upgrades(game):
    state = game.game_state
    plans = []
    COST = { # todo get
        'Caretaker': 3500,
        'SolarPanel': 6800,
        'Insulation': 7200,
        'Playground': 5200,
        'Charger': 3400,
        'Regulator': 1250
    }
    for residence in state.residences:
        if residence.building_name in SETTINGS.UPGRADE.PRIORITY:
            for priority, upgrade_name in enumerate(SETTINGS.UPGRADE.PRIORITY[residence.building_name]):
                if upgrade_name not in residence.effects:
                    if upgrade_name == 'Charger' and SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL and 'Mall.2' not in residence.effects:
                        continue
                    score = 10.0 - priority
                    plan = Plan(Urgency.UPGRADE, score)
                    if state.funds >= SETTINGS.UPGRADE.FUNDS_THRESHOLD and state.funds >= COST[upgrade_name]: # never will happen with high threshold
                        plans.append(plan.upgrade((residence.X, residence.Y), upgrade_name).remember_count(memory, 'upgrade', upgrade_name))
                    elif SETTINGS.UPGRADE.WAIT_FOR_UPGRADE:
                        plans.append(plan.wait())
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

def find_adjust_energy(game):
    plans = []
    ENERGY_CHANGE_COST = 150
    THRESHOLD = 0.001
    def urgency(residence):
        if ENERGY.urgent(residence.temperature):
            return Urgency.MAJOR_ADJUST_ENERGY
        return Urgency.MINOR_ADJUST_ENERGY
    def change(residence, energy):
        return abs(energy - residence.requested_energy_in)
    def score(residence, energy):
        return change(residence, energy) * residence.current_pop
    for residence, energy in recommend_energy_adjustments(game):
        if change(residence, energy) > THRESHOLD:
            plan = Plan(urgency(residence), score(residence, energy))
            if game.game_state.funds < ENERGY_CHANGE_COST:
                plan.wait()
            else:
                plan.adjust_energy((residence.X, residence.Y), energy)
            plans.append(plan)
    return plans
