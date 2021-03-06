class Energy():
    def __init__(self):
        self.DERIVATIVE_NUM_DAYS = 5
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
        self.EXCESSIVE_ENERGY = 50.0
        self.DEPTH = 4
        self.SPAN = 10
    
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
        if 'Insulation' in residence.effects:
            emissivity *= ENERGY.INSULATION_EMISSIVITY_MODIFIER
        if 'Charger' in residence.effects:
            base_energy += ENERGY.CHARGER_BASE_ENERGY_INCREASE
        # the amount of degrees off target through the period
        def score(energy_in):
            def val(temp):
                if temp < ENERGY.TEMP_TOO_LOW:
                    return abs(ENERGY.TEMP_TOO_LOW - temp) + ENERGY.GOOD_MODIFIER * (ENERGY.TEMP_TARGET - ENERGY.TEMP_TOO_LOW)
                elif temp > ENERGY.TEMP_TOO_HIGH:
                    return abs(ENERGY.TEMP_TOO_HIGH - temp) + ENERGY.GOOD_MODIFIER * (ENERGY.TEMP_TOO_HIGH - ENERGY.TEMP_TARGET)
                return ENERGY.GOOD_MODIFIER * abs(ENERGY.TEMP_TARGET - temp)
             # simulate
            total = 0.0
            temp = residence.temperature
            for i in range(ENERGY.FORECAST_DAYS):
                outsideEstimate = estimate_outdoor_temperature_in_days(state, i, outside_temp)
                temp = new_temp(energy_in, base_energy, temp, outsideEstimate, residence.current_pop, emissivity)
                total += val(temp)
            return total
        def search(a, b):
            size = ENERGY.SPAN
            step  = (b - a) / size
            best_score = score(a)
            best_energy = a
            for i in range(size):
                candidate = a + (i + 1) * step
                value = score(candidate)
                if value < best_score: # less is better
                    best_score = value
                    best_energy = candidate
            if best_energy == a:
                return (a, a + step)
            elif best_energy == b:
                return (b - step, b)
            return (best_energy - step, best_energy + step)
        left = base_energy
        right = base_energy + ENERGY.EXCESSIVE_ENERGY
        for i in range(ENERGY.DEPTH):
            left, right = search(left, right)
        return left + (right - left) / 2
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