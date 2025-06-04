import pandas as pd
import os

# Garante que a pasta processed_data exista (compatível com todas as versões de Python)
if not os.path.exists("N:/Quantum_Pong/processed_data"):
    os.makedirs("N:/Quantum_Pong/processed_data")

# 1. Carregar o CSV original
df = pd.read_csv("N:/Quantum_Pong/data/partidas.csv")

# 2. Definir os parâmetros beta (ajuste conforme quiser)
alpha, beta = 75, 25  # Reflete média de 75% SGW em tênis profissional

# 3. Calcular SGW ajustado para cada jogador
df['sgw_jogador1'] = ((df['score_1'] * 0.6 + alpha) / (df['score_1'] + df['score_2'] + alpha + beta)) * 100
df['sgw_jogador2'] = ((df['score_2'] * 0.6 + alpha) / (df['score_1'] + df['score_2'] + alpha + beta)) * 100

# 4. Arredondar para duas casas decimais
df['sgw_jogador1'] = df['sgw_jogador1'].round(2)
df['sgw_jogador2'] = df['sgw_jogador2'].round(2)

# 5. Salvar o novo CSV
df.to_csv("N:/Quantum_Pong/processed_data/partidas_com_sgw.csv", index=False)

print("Colunas 'sgw_jogador1' e 'sgw_jogador2' adicionadas!")
print(df[['id_partida', 'sgw_jogador1', 'sgw_jogador2']].head())
