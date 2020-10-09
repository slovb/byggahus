import sys
import math
import api
from game_layer import GameLayer

with open('apikey.txt','r') as f:
    api_key = f.read().rstrip('\n')
# The different map names can be found on considition.com/rules
map_name = "Gothenburg"  # TODO: You map choice here. If left empty, the map "training1" will be selected.

game = GameLayer(api_key)

def main():
    mode = ""
    if (len(sys.argv) > 1):
        mode = str(sys.argv[1])

    if mode == "reset": killActiveGames()
    elif mode == "info": printGameParameters()

def printGameParameters():
    game.new_game(map_name)
    print("Starting game: " + game.game_state.game_id)
    game.start_game()

    state = game.game_state

    print("max temp: " + str(state.max_temp))
    print("min temp: " + str(state.min_temp))
    print("")

    for residence in state.available_residence_buildings:
        print(residence.building_name + ", released: " + str(residence.release_tick))
    print("")

    for utility in state.available_utility_buildings:
        print(utility.building_name + ", released: " + str(utility.release_tick))
    print("")

    for upg in state.available_upgrades:
        print(upg.name)

    game.end_game()

def killActiveGames():
    games = api.get_games(api_key)
    if not games:
        print("No active games found")
    for g in games:
        if g["active"]:
            api.end_game(api_key, g["gameId"])
            print("Ended game: " + g["gameId"])

if __name__ == "__main__":
    main()
