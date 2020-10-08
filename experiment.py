from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY
import strategy

RUNS = 3
MAP_NAME = 'training2'

if __name__ == "__main__":
    strategy.add_house('ModernApartments')
    strategy.add_house('EnvironmentalHouse')
    strategy.high_rise_availability(350)
    strategy.fill_up(11, 'ModernApartments')
    strategy.cold()
    strategy.open()
 
    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    def nop():
        pass
    def alt():
        SETTINGS.UPGRADE.PRIORITY['EnvironmentalHouse'] = ['SolarPanel']
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
