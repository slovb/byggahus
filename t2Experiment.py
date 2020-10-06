from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY

RUNS = 2
MAP_NAME = 'training2'

if __name__ == "__main__":
    SETTINGS.BUILDING.REQ_MAX_VACANCIES = 14
    SETTINGS.BUILDING.REQ_MIN_HOUSING_QUEUE = 5

    SETTINGS.UPGRADE.FUNDS_THRESHOLD = 23000
    SETTINGS.UPGRADE.SAVE_FOR_UPGRADE = False
    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['SolarPanel', 'Insulation', 'Caretaker', 'Playground', 'Charger'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Caretaker', 'Charger'],
        'EnvironmentalHouse': ['SolarPanel', 'Insulation', 'Caretaker'],
        'LuxuryResidence': ['SolarPanel', 'Caretaker', 'Regulator', 'Playground'],
        'Cabin': [],
        'HighRise': ['Playground', 'Charger', 'Caretaker', 'Insulation']
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = True

    SETTINGS.UTILITY.LIMIT = {
        'Mall': 1,
        'Park': 2,
        'WindTurbine': 0
    }
    SETTINGS.UTILITY.THRESHOLD = 4

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    base = ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator']
    def nop():
        pass
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

    #version = [nop, cCaretaker, cSolarPanel, cInsulation, cPlayground, cCharger, cRegulator]
    version = [cBase, cCaretaker]

    output = []
    for v in version:
        v()
        output += ['------- {} -------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))

