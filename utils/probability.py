import math

def win_probability(qi_index, h2h_score, fatigue_minutes):
    """
    Calcula a probabilidade de vitória baseado nos parâmetros fornecidos.
    Parâmetros:
      qi_index (float): Índice Qi do jogador
      h2h_score (float): Placar ajustado entre os jogadores (head-to-head)
      fatigue_minutes (float): Minutos jogados nos últimos 5 dias
    Retorna:
      float: probabilidade de vitória (0 a 1)
    """
    fatigue_factor = fatigue_minutes / 45
    return 1 / (1 + math.exp(-(0.8*qi_index + 0.5*h2h_score - 0.3*fatigue_factor)))
