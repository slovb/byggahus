from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY

RUNS = 3
MAP_NAME = 'training2'

if __name__ == "__main__":
    SETTINGS.BUILDING.LIMIT = {
        'Apartments': 0,
        'Cabin': 0,
        'EnvironmentalHouse': 1,
        'HighRise': 1,
        'LuxuryResidence': 0,
        'ModernApartments': 9,
    }

    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker', 'Insulation'],
        'HighRise': ['Insulation', 'Caretaker', 'Playground', 'SolarPanel', 'Charger', 'Regulator'],
        'LuxuryResidence': ['Insulation', 'SolarPanel', 'Caretaker', 'Regulator', 'Playground', 'Charger'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker']
    }

    SETTINGS.UTILITY.LIMIT = {
        'Mall': 1,
        'Park': 2,
        'WindTurbine': 2,
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = True

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    SETTINGS.BUILDING.FILL = ['EnvironmentalHouse']

    def nop():
        pass
    def alt():
        SETTINGS.BUILDING.LIMIT['EnvironmentalHouse'] = 3
        SETTINGS.BUILDING.LIMIT['ModernApartments'] = 7
    def reset():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD = 20000
    def grow():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD += 1000

    version = [nop]

    output = []
    for v in version:
        v()
        output += ['--------------------- {} ---------------------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
