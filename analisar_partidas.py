from utils.data_loader import load_csv_partidas
from utils.qi_calculator import calculate_qi
from utils.racket_physics import calculate_rebound
from utils.probability import win_probability
import pandas as pd

def main():
    # 1. Carrega o CSV
    df = load_csv_partidas()
    if df is None:
        print("Arquivo de dados não encontrado ou está vazio!")
        return

    # 2. Faz o cálculo do Qi Index para cada linha
    try:
        df['qi_index'] = df.apply(lambda row: calculate_qi(
            row['forehand_spin'],
            row['backhand_stability'],
            row['fatigue'],
            row['pressure']
        ), axis=1)
    except Exception as e:
        print("Erro ao calcular Qi Index:", e)
        return

    # 3. Calcula o rebound da raquete
    try:
        df['rebound'] = df.apply(lambda row: calculate_rebound(
            row['incoming_angle'],
            row['rubber_hardness']
        ), axis=1)
    except Exception as e:
        print("Erro ao calcular Rebound:", e)
        return

    # 4. Calcula a probabilidade de vitória
    try:
        df['prob_win'] = df.apply(lambda row: win_probability(
            df['qi_index'][row.name],    # já calculado acima
            row['h2h_score'],
            row['fatigue_minutes']
        ), axis=1)
    except Exception as e:
        print("Erro ao calcular Probabilidade de Vitória:", e)
        return

    # 5. Salva os resultados na pasta processed_data
    output_path = "processed_data/partidas_analisadas.csv"
    df.to_csv(output_path, index=False)
    print(f"Análise finalizada! Resultados salvos em {output_path}")
    print(df[['id_partida', 'qi_index', 'rebound', 'prob_win']].head())  # Mostra só os primeiros

if __name__ == "__main__":
    main()
