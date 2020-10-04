# bundling the energy solver in one file
from tools.newtonRaphson import find_root, dfdx

class Energy():
    def __init__(self):
        self.DERIVATIVE_NUM_DAYS = 5
        self.H = 0.001
        self.DEG_PER_EXCESS_MWH = 0.75
        self.DEG_PER_POP = 0.04
        self.FORECAST_DAYS = 15
        self.TEMP_TARGET = 21.0
        self.TEMP_TOO_LOW = 18.5
        self.TEMP_TOO_HIGH = 23.5
        self.INSULATION_EMISSIVITY_MODIFIER = 0.6
        self.CHARGER_BASE_ENERGY_INCREASE = 1.8
        self.GOOD_MODIFIER = 0.1
        self.LENGTH_OF_YEAR = 183
    
    def urgent(self, temperature):
        return temperature < self.TEMP_TOO_LOW or temperature > self.TEMP_TOO_HIGH

ENERGY = Energy()
temperature = []

# run this before repeated runs
def reset_temperature_memory():
    temperature.clear()

# run this at the start of every turn
def memorize_temperature(temp):
    temperature.append(temp)

def recommend_energy_adjustments(game):
    def temperature_derivative():
        t = temperature
        if len(t) == 0 or len(t) == 1:
            return 0.0
        elif len(t) < ENERGY.DERIVATIVE_NUM_DAYS:
            return (t[-1] - t[0]) / (len(t) - 1)
        return (t[-1] - t[-ENERGY.DERIVATIVE_NUM_DAYS]) / (ENERGY.DERIVATIVE_NUM_DAYS - 1)


    def estimate_outdoor_temperature_in_days(state, i, outside_temp):
        if state.turn > ENERGY.LENGTH_OF_YEAR:
            return temperature[(state.turn + i) % ENERGY.LENGTH_OF_YEAR]
        return outside_temp + i * temperature_derivative()

    def new_temp(energy_in, base_energy, indoor_temperature, outdoor_temperature, current_pop, emissivity):
        return indoor_temperature + (energy_in - base_energy) * ENERGY.DEG_PER_EXCESS_MWH + ENERGY.DEG_PER_POP * current_pop - (indoor_temperature - outdoor_temperature) * emissivity
    
    state = game.game_state
    def get_energy_need(residence):
        outside_temp = state.current_temp
        bp = game.get_residence_blueprint(residence.building_name)
        base_energy = bp.base_energy_need
        emissivity = bp.emissivity
        for name in residence.effects:
            if name == 'Insulation':
                emissivity *= ENERGY.INSULATION_EMISSIVITY_MODIFIER
            elif name == 'Charger':
                base_energy += ENERGY.CHARGER_BASE_ENERGY_INCREASE
        # the amount of degrees off target through the period
        def score(energy_in):
            def val(temp):
                if temp < ENERGY.TEMP_TOO_LOW:
                    return abs(ENERGY.TEMP_TOO_LOW - temp) + ENERGY.GOOD_MODIFIER * (ENERGY.TEMP_TARGET - ENERGY.TEMP_TOO_LOW)
                elif temp > ENERGY.TEMP_TOO_HIGH:
                    return abs(ENERGY.TEMP_TOO_HIGH - temp) + ENERGY.GOOD_MODIFIER * (ENERGY.TEMP_TOO_HIGH - ENERGY.TEMP_TARGET)
                return ENERGY.GOOD_MODIFIER * abs(ENERGY.TEMP_TARGET - temp)
            total = 0.0
            temp = residence.temperature
            for i in range(ENERGY.FORECAST_DAYS):
                outsideEstimate = estimate_outdoor_temperature_in_days(state, i, outside_temp)
                temp = new_temp(energy_in, base_energy, temp, outsideEstimate, residence.current_pop, emissivity)
                total += val(temp)
            return total
        def guess_start():
            return base_energy + (ENERGY.TEMP_TARGET - residence.temperature + ENERGY.DEG_PER_POP * residence.current_pop + (residence.temperature - outside_temp) * emissivity) / ENERGY.DEG_PER_EXCESS_MWH
        # trying to minimize a strictly positive function, so take the derivative
        f = lambda energy_in: dfdx(score, energy_in, ENERGY.H)
        guess = guess_start() - 5.0*ENERGY.H
        energy = find_root(score, guess, ENERGY.H)
        return max(base_energy, energy)
    recommendations = []
    for residence in state.residences:
        need = get_energy_need(residence)
        recommendations.append((residence, need))
    return recommendations

def best_recommendation(game):
    importance = (False, 0.0)
    best = None
    def change(residence, energy):
        return abs(energy - residence.requested_energy_in)
    def score(residence, energy):
        return change(residence, energy) * residence.current_pop
    for residence, energy in recommend_energy_adjustments(game):
        i = (ENERGY.urgent(residence.temperature), score(residence, energy))
        if i > importance:
            importance = i
            best = (residence, energy)
    return best