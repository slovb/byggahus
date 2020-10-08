from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, forget, pretty
from tools.dirtyRegulator import ENERGY
import strategy

RUNS = 3
MAP_NAME = 'training1'

if __name__ == "__main__":
    strategy.add_house('LuxuryResidence', 7)
    strategy.add_house('ModernApartments')
    strategy.add_house('EnvironmentalHouse')
    strategy.high_rise_availability(0)
    strategy.fill_up(11, 'ModernApartments')
    strategy.warm()
    strategy.closed()
    strategy.open_with('LuxuryResidence')

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    def nop():
        pass
    def alt():
        #SETTINGS.UPGRADE.PRIORITY['EnvironmentalHouse'] = ['SolarPanel']
        SETTINGS.UPGRADE.PRIORITY['LuxuryResidence'] = ['SolarPanel']
        SETTINGS.UPGRADE.LOW_PRIORITY['LuxuryResidence'] = ['Playground', 'Insulation', 'Caretaker', 'Regulator',  'Charger']
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
