from solvers.experiment import setup, take_turn, SETTINGS
from solver import main, pretty, forget
from tools.dirtyRegulator import ENERGY
import strategy

RUNS = 1
MAP_NAME = 'Gothenburg'

def add(name, amount = 1):
    return lambda: strategy.add_house(name, amount)

def cc(*funcs):
    def h():
        for f in funcs:
            f()
    return h

if __name__ == "__main__":
    strategy.add_house('LuxuryResidence', 7)
    strategy.add_house('Apartments')
    strategy.add_house('EnvironmentalHouse')
    strategy.high_rise_availability(250)
    strategy.diversify()
    #strategy.fill_up(11, 'Apartments')
    strategy.fill_up(11, 'EnvironmentalHouse')
    strategy.warm()
    strategy.open()
    strategy.open_with('LuxuryResidence')
    SETTINGS.BUILDING.JUST_BUILD = False

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
        SETTINGS.MAINTENANCE.THRESHOLD['Other'] = 37
    def grow():
        SETTINGS.MAINTENANCE.THRESHOLD['Other'] += 1


    version = [nop]

    output = []
    for v in version:
        v()
        output += ['--------------------- {} ---------------------'.format(v.__name__)]
        scores = [main(MAP_NAME, setup, take_turn) for i in range(RUNS)]
        output += [' ', pretty(), ' ', bottom(scores)]
        forget()
    print('\n'.join(output))
