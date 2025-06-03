import math

def calculate_qi(forehand_spin, backhand_stability, fatigue, pressure):
    """
    Calcula o índice Qi simplificado para uma partida de tênis de mesa.

    Parâmetros:
    - forehand_spin (float): Valor do spin do forehand do jogador
    - backhand_stability (float): Estabilidade do backhand do jogador
    - fatigue (float): Fadiga estimada do jogador
    - pressure (float): Pressão/estresse em pontos críticos

    Retorna:
    - float: Qi Index
    """
    numerator = 0.7 * forehand_spin + 0.3 * backhand_stability
    denominator = math.sqrt(fatigue**2 + 0.5 * pressure**2)
    return numerator / denominator if denominator != 0 else 0
