from solvers.experiment import setup, take_turn, SETTINGS
from solver import main

if __name__ == "__main__":
    #SETTINGS.BUILDING.LIMIT_RESIDENCES = 2
    scores = [main("training2", setup, take_turn) for i in range(10)]
    print(scores)
    print('Max: {}\tAvg: {}'.format(max(scores), sum(scores) / len(scores)))
