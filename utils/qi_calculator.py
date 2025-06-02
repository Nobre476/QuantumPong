# N:\Quantum_Pong\utils\qi_calculator.py
import math

def calculate_qi(forehand_spin, backhand_stability, fatigue, pressure):
    """
    Calcula o índice Qi - versão simplificada para iniciantes
    Valores de exemplo:
    - forehand_spin: 1 a 10 (habilidade do jogador)
    - backhand_stability: 1 a 10 
    - fatigue: 1 a 10 (cansaço)
    - pressure: 1 a 10 (pressão psicológica)
    """
    numerator = 0.7 * forehand_spin + 0.3 * backhand_stability
    denominator = math.sqrt(fatigue**2 + 0.5 * pressure**2)
    qi = numerator / denominator if denominator != 0 else 0
    return round(qi, 2)