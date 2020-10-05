from solvers.utilities import setup, take_turn, SETTINGS
from solver import main, pretty_print

if __name__ == "__main__":
    SETTINGS.BUILDING.REQ_MAX_VACANCIES = 14
    SETTINGS.BUILDING.REQ_MIN_HOUSING_QUEUE = 5

    SETTINGS.UPGRADE.FUNDS_THRESHOLD = 23000
    SETTINGS.UPGRADE.WAIT_FOR_UPGRADE = False
    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['SolarPanel', 'Insulation', 'Caretaker', 'Playground', 'Charger'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Caretaker', 'Charger'],
        'EnvironmentalHouse': ['SolarPanel', 'Insulation', 'Caretaker'],
        'LuxuryResidence': ['SolarPanel', 'Caretaker', 'Regulator', 'Playground'],
        'Cabin': [],
        'HighRise': ['Playground', 'Charger', 'Caretaker', 'Insulation']
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = True

    scores = [main("training2", setup, take_turn) for i in range(5)]
    print(' ')
    pretty_print()
    print(' ')
    print('Max: {}\tAvg: {}'.format(max(scores), sum(scores) / len(scores)))
