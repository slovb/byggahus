from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, forget, pretty
from tools.dirtyRegulator import ENERGY

RUNS = 3
MAP_NAME = 'training1'

if __name__ == "__main__":
    SETTINGS.BUILDING.LIMIT = {
        'Apartments': 0,
        'Cabin': 0,
        'EnvironmentalHouse': 1,
        'HighRise': 8,
        'LuxuryResidence': 7,
        'ModernApartments': 1,
    }

    SETTINGS.UPGRADE.PRIORITY = {
        'Apartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'Cabin': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
        'EnvironmentalHouse': ['SolarPanel', 'Insulation', 'Regulator', 'Caretaker', 'Playground'],
        'HighRise': ['SolarPanel', 'Playground', 'Regulator', 'Caretaker', 'Insulation', 'Charger'],
        'LuxuryResidence': ['Insulation', 'SolarPanel', 'Caretaker', 'Regulator', 'Playground'],
        'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker']
    }
    
    SETTINGS.UTILITY.LIMIT = {
        'Mall': 0,
        'Park': 1,
        'WindTurbine': 2,
    }
    SETTINGS.UPGRADE.CHARGER_ONLY_ON_MALL = False

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    def nop():
        pass
    def alt():
        SETTINGS.UPGRADE.PRIORITY['EnvironmentalHouse'] = ['SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker', 'Insulation']
    def reset():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD = 20000
    def grow():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD += 1000

    version = [nop, alt]

    output = []
    for v in version:
        v()
        output += ['--------------------- {} ---------------------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
