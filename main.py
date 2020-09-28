import sys
import math
import api
from game_layer import GameLayer

with open('apikey.txt','r') as f:
    api_key = f.read()
# The different map names can be found on considition.com/rules
map_name = "training1"  # TODO: You map choice here. If left empty, the map "training1" will be selected.

game = GameLayer(api_key)

DEG_PER_EXCESS_MWH = 0.75
DEG_PER_POP = 0.04


def main():
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

        getInfo()
        game.end_game()

    else:
        game.new_game(map_name)
        print("Starting game: " + game.game_state.game_id)
        game.start_game()

        totalQueueHappiness = 0.0

        while game.game_state.turn < game.game_state.max_turns:
            state = game.game_state
            happinessLastTurn = state.total_happiness

            take_turn()

            state = game.game_state
            for message in state.messages:
                print(message + " " + "Happiness: " + str(state.total_happiness) + 
                    ", Growth " + str(state.total_happiness - happinessLastTurn) + 
                    ", Q-growth " + str(state.queue_happiness))
            for error in state.errors:
                print("Error: " + error)

            totalQueueHappiness += game.game_state.queue_happiness
            

        score = str(game.get_score()["finalScore"])

        print("Done with game: " + game.game_state.game_id)
        print("Remaining cash: " + str(math.floor(game.game_state.funds)))
        print("Scoring: Population: " + str(15 * int(game.get_score()["finalPopulation"])) + " (pop: " + str(game.get_score()["finalPopulation"]) + 
            "), happiness: " + str(math.floor(game.get_score()["totalHappiness"] / 10)) + 
            " (queue: " + str(math.floor(totalQueueHappiness / 10)) +
            ") and co2: -" + str(game.get_score()["totalCo2"]))
        print("Final score was: " + score)


def getInfo():
    state = game.game_state

    for residence in state.available_residence_buildings:
        print(residence.building_name)

    for upg in state.available_upgrades:
        print(upg.name)

    #for upg in state.available_upgrades:
    #    print(upg.name + " " + upg.effect + " " + str(upg.cost))




def take_turn():
    # TODO Implement your artificial intelligence here.
    # TODO Take one action per turn until the game ends.

    state = game.game_state

    # continue construction?
    for residence in state.residences:
        if residence.build_progress < 100:
            game.build((residence.X, residence.Y))
            return

    # new construction?
    building_name = "Apartments"
    pop_tot = 0
    pop_cap = 0
    for residence in state.residences:
        pop_tot += residence.current_pop
        pop_cap += game.get_blueprint(building_name).max_pop
    if (state.funds >= game.get_blueprint(building_name).cost and 
        state.housing_queue >= 14 and
        pop_cap - pop_tot <= 5):
        for i in range(len(state.map)):
            for j in range(len(state.map)):
                if state.map[i][j] == 0:
                    plotTaken = False
                    for residence in state.residences:
                        if residence.X == i and residence.Y == j:
                            plotTaken = True
                            break
                    if not plotTaken:
                        x = i
                        y = j
                        game.place_foundation((x, y), building_name)
                        return

    # upgrades?
    for residence in state.residences:
        upgrade = next((upgrade for upgrade in state.available_upgrades if upgrade.name == "Caretaker"), None)
        if upgrade is not None and "Caretaker" not in residence.effects and state.funds >= upgrade.cost:
            game.buy_upgrade((residence.X, residence.Y), "Caretaker")
            return
        upgrade = next((upgrade for upgrade in state.available_upgrades if upgrade.name == "SolarPanel"), None)
        if upgrade is not None and "SolarPanel" not in residence.effects and state.funds >= upgrade.cost:
            game.buy_upgrade((residence.X, residence.Y), "SolarPanel")
            return

    # maintenance?
    for residence in state.residences:
        if residence.health < 50:
            game.maintenance((residence.X, residence.Y))
            return
    
    # cold house?
    for residence in state.residences:
        if residence.temperature < 18:
            energy = getEnergyNeed(residence, state.current_temp)
            game.adjust_energy_level((residence.X, residence.Y), energy)
            return
        elif residence.temperature > 24:
            blueprint = game.get_residence_blueprint(residence.building_name)
            energy = blueprint.base_energy_need - 0.5 \
                     + (residence.temperature - state.current_temp) * blueprint.emissivity / 1 \
                     - residence.current_pop * 0.04
            game.adjust_energy_level((residence.X, residence.Y), energy)
            return

    game.wait()


def getEnergyNeed(residence, outsideTemp):
    bp = game.get_residence_blueprint(residence.building_name)

    # Follows the following formula:
    # energy_need = base_energy + (21 - inside_temp - 0.04 * pop + (inside_temp - outside_temp) * emissivity) * 0.75
    return bp.base_energy_need + (21 - residence.temperature - DEG_PER_POP * residence.current_pop + (residence.temperature - outsideTemp) * bp.emissivity)/DEG_PER_EXCESS_MWH



if __name__ == "__main__":
    main()