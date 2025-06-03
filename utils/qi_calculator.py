import math

def calculate_qi(forehand_spin, backhand_stability, fatigue, pressure):
    """Versão nova que retorna Qi E estado"""
    numerator = 0.7 * forehand_spin + 0.3 * backhand_stability
    denominator = math.sqrt(fatigue**2 + 0.5 * pressure**2 + 1e-6)
    qi_value = numerator / denominator

    if qi_value > 1.15:
        state = "Flow State"
    elif qi_value > 0.85:
        state = "Optimal Performance"
    elif qi_value > 0.6:
        state = "Normal"
    else:
        state = "Below Par"
    
    return qi_value, state  # Agora retorna DOIS valores!