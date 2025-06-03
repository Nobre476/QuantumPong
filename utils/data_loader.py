import pandas as pd

def load_csv_partidas(path="N:/Quantum_Pong/data/partidas.csv"):
    try:
        df = pd.read_csv(path)
        print(f"{len(df)} partidas carregadas.")
        return df
    except FileNotFoundError:
        print("Arquivo não encontrado:", path)
        return None
