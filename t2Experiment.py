from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY
import strategy

RUNS = 1
MAP_NAME = 'training2'

if __name__ == "__main__":
    strategy.add_house('Apartments', 3)
    strategy.add_house('ModernApartments')
    strategy.add_house('EnvironmentalHouse')
    strategy.high_rise_availability(350)
    strategy.fill_up(12, 'ModernApartments')
    strategy.cold()
    strategy.open()
    strategy.diversify()
 
    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    def nop():
        pass
    def less():
        SETTINGS.BUILDING.LIMIT_RESIDENCES -= 2
    def alt():
        SETTINGS.UPGRADE.SAVE_FOR_UPGRADE = True
    def altUp():
        SETTINGS.UPGRADE.PRIORITY = {
            'Apartments': ['SolarPanel', 'Insulation'],
            'Cabin': ['Insulation', 'SolarPanel'],
            'EnvironmentalHouse': ['SolarPanel'],
            'HighRise': ['Insulation', 'SolarPanel'],
            'LuxuryResidence': ['Insulation', 'SolarPanel'],
            'ModernApartments': ['Insulation', 'SolarPanel'],
        }
        SETTINGS.UPGRADE.LOW_PRIORITY = {
            'Apartments': ['Playground', 'Charger', 'Regulator', 'Caretaker'],
            'Cabin': ['Playground', 'Charger', 'Regulator', 'Caretaker'],
            'EnvironmentalHouse': ['Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker'],
            'HighRise': ['Playground', 'Caretaker', 'Charger', 'Regulator'],
            'LuxuryResidence': ['Playground', 'Caretaker', 'Regulator', 'Charger'],
            'ModernApartments': ['Playground', 'Charger', 'Regulator', 'Caretaker'],
        }
    def alt2():
        SETTINGS.UPGRADE.PRIORITY = {
            'Apartments': ['SolarPanel', 'Insulation', 'Playground', 'Charger', 'Regulator', 'Caretaker'],
            'Cabin': ['Insulation', 'SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker'],
            'EnvironmentalHouse': ['SolarPanel', 'Playground', 'Insulation', 'Charger', 'Regulator', 'Caretaker'],
            'HighRise': ['Insulation', 'SolarPanel', 'Playground', 'Caretaker', 'Charger', 'Regulator'],
            'LuxuryResidence': ['Insulation', 'SolarPanel', 'Playground', 'Caretaker', 'Regulator', 'Charger'],
            'ModernApartments': ['Insulation', 'SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker'],
        }
        SETTINGS.UPGRADE.LOW_PRIORITY = {
            'Apartments': [],
            'Cabin': [],
            'EnvironmentalHouse': [],
            'HighRise': [],
            'LuxuryResidence': [],
            'ModernApartments': [],
        }
    def alt3():
        SETTINGS.UPGRADE.CHARGER_PRIO_ON_MALL = False
        '''
        SETTINGS.UPGRADE.PRIORITY = {
            'Apartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
            'Cabin': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker'],
            'EnvironmentalHouse': ['SolarPanel', 'Playground', 'Charger', 'Regulator', 'Caretaker', 'Insulation'],
            'HighRise': ['Insulation', 'Caretaker', 'Playground', 'SolarPanel', 'Charger', 'Regulator'],
            'LuxuryResidence': ['Insulation', 'SolarPanel', 'Caretaker', 'Regulator', 'Playground', 'Charger'],
            'ModernApartments': ['Insulation', 'Playground', 'SolarPanel', 'Charger', 'Regulator', 'Caretaker']
        }
        '''
    def no_mall():
        SETTINGS.UTILITY.LIMIT['Mall'] = 0
        
    def reset():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD = 20000
    def grow():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD += 1000

    version = [nop, no_mall]

    output = []
    for v in version:
        v()
        output += ['--------------------- {} ---------------------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
