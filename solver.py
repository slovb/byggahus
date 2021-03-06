import sys
import math
import api
from game_layer import GameLayer
import traceback

with open('apikey.txt','r') as f:
    api_key = f.read().rstrip('\n')
game = GameLayer(api_key)

memory = []
def main(map_name, setup, take_turn):
    mode = ""
    if (len(sys.argv) > 1):
        mode = str(sys.argv[1])
    if mode == "reset":
        games = api.get_games(api_key)
        for g in games:
            if g["active"]:
                api.end_game(api_key, g["gameId"])
                print("Ended game: " + g["gameId"])
    elif mode == "test":
        game.new_game(map_name)
        print("Starting game: " + game.game_state.game_id)
        game.start_game()
        get_info()
        game.end_game()
    else:
        game.new_game(map_name)
        print("Starting game: " + game.game_state.game_id)
        game.start_game()
        total_queue_happiness = 0.0
        setup(game) # initial setup
        turn_info = None
        while game.game_state.turn < game.game_state.max_turns:
            state = game.game_state
            happiness_last_turn = state.total_happiness
            try:
                turn_info = take_turn(game) # take turn
            except Exception as ex:
                print(traceback.format_exc())
                print(ex)
                game.end_game()
                return -1
            state = game.game_state
            for message in state.messages:
                print(message + " " + "Happiness: " + str(math.floor(state.total_happiness)) +
                    ", Growth " + str(math.floor(state.total_happiness - happiness_last_turn)) +
                    ", Q-growth " + str(math.floor(state.queue_happiness)))
            for error in state.errors:
                print("Error: " + error)
            total_queue_happiness += game.game_state.queue_happiness
        score = str(game.get_score()["finalScore"])
        print("Done with game: " + game.game_state.game_id)
        print("Remaining cash: " + str(math.floor(game.game_state.funds)))
        print("Scoring: Population: " + str(15 * int(game.get_score()["finalPopulation"])) + " (pop: " + str(game.get_score()["finalPopulation"]) +
            "), happiness: " + str(math.floor(game.get_score()["totalHappiness"] / 10)) +
            " (queue: " + str(math.floor(total_queue_happiness / 10)) +
            ") and co2: -" + str(game.get_score()["totalCo2"]))
        print("Final score was: " + score)
        if turn_info is not None:
            for k, v in sorted(turn_info.items(), key=lambda item: item[1], reverse=True):
                print('{}\t{}\t{}'.format(str(v), str(k[0]), str(k[1])))
        memory.append((int(score), game.game_state.game_id))
        return int(score)
    return None

def pretty():
    return '\n'.join(['{}\t{}'.format(score, id) for score, id in memory])

def pretty_print():
    print(pretty())

def forget():
    memory.clear()

def get_info():
    state = game.game_state

    for residence in state.available_residence_buildings:
        print(residence.building_name)

    for upg in state.available_upgrades:
        print(upg.name)

    #for upg in state.available_upgrades:
    #    print(upg.name + " " + upg.effect + " " + str(upg.cost))
