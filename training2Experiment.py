from solvers.experiment import setup, take_turn
from solver import main

if __name__ == "__main__":
    scores = [main("training2", setup, take_turn) for i in range(5)]
    print(scores)
    print('Max: {}\tAvg: {}'.format(max(scores), sum(scores) / len(scores)))