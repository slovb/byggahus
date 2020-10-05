from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty_print

if __name__ == "__main__":
    SETTINGS.BUILDING.REQ_MAX_VACANCIES = 10
    SETTINGS.BUILDING.REQ_MIN_HOUSING_QUEUE = 5
    SETTINGS.BUILDING.PRIORITY = [
        'HighRise',
        'LuxuryResidence',
        'EnvironmentalHouse',
        'Apartments',
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
    SETTINGS.UPGRADE.WAIT_FOR_UPGRADE = False

    SETTINGS.UTILITY.LIMIT = {
        'Mall': 0,
        'Park': 1,
        'WindTurbine': 1
    }
    SETTINGS.UTILITY.THRESHOLD = 3

    scores = [main("training1", setup, take_turn) for i in range(5)]
    print(' ')
    pretty_print()
    print(' ')
    print('Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores)))
