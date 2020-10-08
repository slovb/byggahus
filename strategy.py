from tools.dirtyRegulator import ENERGY
from solvers.experiment import SETTINGS

def add_house(house, n = 1):
    SETTINGS.BUILDING.LIMIT[house] += n

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
        'Apartments': ['Insulation', 'SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Insulation', 'SolarPanel'],
        'EnvironmentalHouse': ['SolarPanel'],
        'HighRise': ['Insulation', 'SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker'],
        'LuxuryResidence': ['SolarPanel', 'Playground', 'Insulation', 'Caretaker', 'Regulator',  'Charger'],
        'ModernApartments': ['SolarPanel', 'Playground', 'Insulation', 'Caretaker', 'Regulator',  'Charger'],
    }
    SETTINGS.UPGRADE.LOW_PRIORITY = {
        'Apartments': [],
        'Cabin': ['Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker', ],
        'HighRise': [],
        'LuxuryResidence': [],
        'ModernApartments': [],
    }

def cold():
    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Insulation', 'SolarPanel'],
        'EnvironmentalHouse': ['SolarPanel'],
        'HighRise': ['Insulation', 'Playground', 'SolarPanel', 'Caretaker', 'Charger', 'Regulator'],
        'LuxuryResidence': ['Insulation', 'SolarPanel', 'Caretaker', 'Regulator', 'Playground', 'Charger'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
    }
    SETTINGS.UPGRADE.LOW_PRIORITY = {
        'Apartments': [],
        'Cabin': ['Playground', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker'],
        'HighRise': [],
        'LuxuryResidence': [],
        'ModernApartments': [],
    }

def closed():
    SETTINGS.UTILITY.LIMIT = {
        'Mall': 0,
        'Park': 1,
        'WindTurbine': 2,
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = False

def open():
    SETTINGS.UTILITY.LIMIT = {
        'Mall': 1,
        'Park': 2,
        'WindTurbine': 2,
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = True