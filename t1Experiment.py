from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, forget, pretty
from tools.dirtyRegulator import ENERGY

RUNS = 2
MAP_NAME = 'training1'

if __name__ == "__main__":
    SETTINGS.BUILDING.REQ_MAX_VACANCIES = 10
    SETTINGS.BUILDING.REQ_MIN_HOUSING_QUEUE = 5
    SETTINGS.BUILDING.PRIORITY = [
        'HighRise',
        'LuxuryResidence',
        'Apartments',
        'EnvironmentalHouse',
        'Cabin',
        'ModernApartments'
    ]
    SETTINGS.BUILDING.LIMIT_RESIDENCES = 18
    SETTINGS.BUILDING.LIMIT = {
        'Apartments': 0,
        'Cabin': 0,
        'EnvironmentalHouse': 3,
        'HighRise': 6,
        'LuxuryResidence': 9,
        'ModernApartments': 0
    }
    SETTINGS.BUILDING.DELAY = {
        'HighRise': 120,
    }
    SETTINGS.BUILDING.FILL = ['EnvironmentalHouse']

    SETTINGS.UPGRADE.FUNDS_THRESHOLD = 23000
    SETTINGS.UPGRADE.PRIORITY = {
        'LuxuryResidence': ['SolarPanel', 'Caretaker', 'Insulation', 'Regulator', 'Playground'],
        'HighRise': ['SolarPanel', 'Regulator', 'Playground', 'Caretaker', 'Insulation', 'Charger'],
        'EnvironmentalHouse': ['SolarPanel', 'Caretaker', 'Insulation', 'Regulator', 'Playground']
    }
    SETTINGS.UPGRADE.SAVE_FOR_UPGRADE = False
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = False

    SETTINGS.UTILITY.LIMIT = {
        'Mall': 0,
        'Park': 1,
        'WindTurbine': 1
    }
    SETTINGS.UTILITY.THRESHOLD = 3

    #ENERGY.FORECAST_DAYS = 20
    #ENERGY.TEMP_TOO_HIGH = 22.0
    #ENERGY.TEMP_TOO_LOW = 20.0
    #SETTINGS.ENERGY.THRESHOLD = 0.01
    SETTINGS.MINOR_FUNDS_LIMIT = 0
    SETTINGS.MINOR_INCOME_LIMIT = 0

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))
     

    '''
    base = ['Playground', 'SolarPanel', 'Caretaker', 'Insulation']
    def cBase():
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base
    def cCaretaker():
        a = 'Caretaker'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]
    def cSolarPanel():
        a = 'SolarPanel'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]
    def cInsulation():
        a = 'Insulation'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]
    def cPlayground():
        a = 'Playground'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]
    def cCharger():
        a = 'Caretaker'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]
    def cRegulator():
        a = 'Caretaker'
        for k in SETTINGS.UPGRADE.PRIORITY:
            SETTINGS.UPGRADE.PRIORITY[k] = base + [a]

    version = [cBase, cCharger, cRegulator]
    '''


    def nop():
        pass
    def alt():
        SETTINGS.UPGRADE.PRIORITY = {
            'LuxuryResidence': ['Playground', 'SolarPanel', 'Regulator', 'Caretaker', 'Insulation'],
            'HighRise': ['Playground', 'SolarPanel', 'Regulator', 'Caretaker', 'Insulation'],
            'EnvironmentalHouse': ['Playground', 'SolarPanel', 'Regulator', 'Caretaker', 'Insulation']
        }
    def regulated():
        SETTINGS.UPGRADE.PRIORITY = {
            'LuxuryResidence': ['Playground', 'SolarPanel', 'Caretaker', 'Insulation', 'Regulator'],
            'HighRise': ['Playground', 'SolarPanel', 'Caretaker', 'Insulation', 'Regulator'],
            'EnvironmentalHouse': ['Playground', 'SolarPanel', 'Caretaker', 'Insulation', 'Regulator']
        }

    version = [nop, alt, regulated]

    output = []
    for v in version:
        v()
        output += ['------- {} -------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
