from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY
import strategy

RUNS = 1
MAP_NAME = 'training1'

def add(name, amount = 1):
    return lambda: strategy.add_house(name, amount)

def cc(*funcs):
    def h():
        for f in funcs:
            f()
    return h

if __name__ == "__main__":
    strategy.add_house('LuxuryResidence', 7)
    strategy.add_house('ModernApartments')
    strategy.add_house('EnvironmentalHouse')
    strategy.high_rise_availability(0)
    #strategy.diversify()
    strategy.fill_up(11, 'ModernApartments')
    strategy.warm()
    strategy.closed()
    strategy.open_with('LuxuryResidence')

    def bottom(scores):
        return 'Max: {}\tAvg: {:10.2f}'.format(max(scores), sum(scores) / len(scores))

    def nop():
        pass
    def alt():
        SETTINGS.UPGRADE.SAVE_FOR_UPGRADE = True
    def reprio():
        name = 'HighRise'
        SETTINGS.UPGRADE.LOW_PRIORITY[name].insert(0, SETTINGS.UPGRADE.PRIORITY[name].pop())
    def reset():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD = 20000
    def grow():
        SETTINGS.UPGRADE.FUNDS_THRESHOLD += 1000

    version = [nop]
    #version = [nop] + [add('HighRise')] * 2 + [combo(add('HighRise'), add('ModernApartments', -1))]

    output = []
    for v in version:
        v()
        output += ['--------------------- {} ---------------------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
