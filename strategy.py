from tools.dirtyRegulator import ENERGY
from solvers.experiment import SETTINGS

def add_house(house, n = 1):
    SETTINGS.BUILDING.LIMIT[house] += n

def open_with(house, n = None):
    if n == None:
        n = SETTINGS.BUILDING.LIMIT[house]
    SETTINGS.BUILDING.OPENER += [house] * n

def high_rise_availability(turn):
    n = max(0, (400 - turn) // 50)
    SETTINGS.BUILDING.LIMIT['HighRise'] = n

def fill_up(count, house):
    n = max(0, count - sum(SETTINGS.BUILDING.LIMIT.values()))
    SETTINGS.BUILDING.LIMIT[house] += n

def diversify():
    for k in SETTINGS.BUILDING.LIMIT:
        v = SETTINGS.BUILDING.LIMIT[k]
        SETTINGS.BUILDING.LIMIT[k] = max(1, v)
    SETTINGS.BUILDING.DIVERSIFY = True

def warm():
    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['Insulation', 'SolarPanel', 'Playground'],
        'Cabin': ['Insulation', 'SolarPanel'],
        'EnvironmentalHouse': ['SolarPanel'],
        'HighRise': ['Insulation', 'SolarPanel', 'Playground', 'Charger'],
        'LuxuryResidence': ['SolarPanel', 'Playground'],
        'ModernApartments': ['SolarPanel', 'Playground'],
    }
    SETTINGS.UPGRADE.LOW_PRIORITY = {
        'Apartments': ['Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker', ],
        'HighRise': ['Regulator', 'Caretaker'],
        'LuxuryResidence': ['Insulation', 'Caretaker', 'Regulator',  'Charger'],
        'ModernApartments': ['Insulation', 'Caretaker', 'Regulator',  'Charger'],
    }

def cold():
    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['Insulation', 'Playground', 'SolarPanel'],
        'Cabin': ['Insulation', 'SolarPanel'],
        'EnvironmentalHouse': ['SolarPanel'],
        'HighRise': ['Insulation', 'Playground', 'SolarPanel'],
        'LuxuryResidence': ['Insulation', 'SolarPanel', 'Playground'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel'],
    }
    SETTINGS.UPGRADE.LOW_PRIORITY = {
        'Apartments': ['Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Playground', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker'],
        'HighRise': ['Caretaker', 'Charger', 'Regulator'],
        'LuxuryResidence': ['Caretaker', 'Regulator', 'Charger'],
        'ModernApartments': ['Charger', 'Regulator', 'Caretaker'],
    }

def closed():
    SETTINGS.UTILITY.LIMIT = {
        'Mall': 0,
        'Park': 1,
        'WindTurbine': 2,
    }

def open():
    SETTINGS.UTILITY.LIMIT = {
        'Mall': 1,
        'Park': 2,
        'WindTurbine': 2,
    }
