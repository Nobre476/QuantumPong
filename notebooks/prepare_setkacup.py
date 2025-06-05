import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import LabelEncoder

# 1. Carregar os dados brutos (ajustado para seu caminho)
df = pd.read_csv('../data/integrado_setkacup.csv')

# 2. Converter scores para número
df['score_1'] = pd.to_numeric(df['score_1'], errors='coerce')
df['score_2'] = pd.to_numeric(df['score_2'], errors='coerce')

# 3. Extrair total de pontos do campo 'sets'
def extrai_total_pontos(sets_str):
    if pd.isnull(sets_str):
        return np.nan
    numeros = [int(x) for x in re.findall(r'\d+', sets_str)]
    return sum(numeros) if numeros else np.nan

df['total_pontos'] = df['sets'].apply(extrai_total_pontos)

# 4. Criar targets
df['target_over_79_5'] = (df['total_pontos'] > 79.5).astype(int)
df['target_vencedor'] = (df['score_1'] > df['score_2']).astype(int)

# 5. Criar idade dos jogadores
df['idade_jogador1'] = 2025 - pd.to_numeric(df['year of birth'], errors='coerce')

# 6. Extrair features de data
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['mes'] = df['data'].dt.month
df['ano'] = df['data'].dt.year
df['dia_semana'] = df['data'].dt.dayofweek

# 7. Codificar colunas categóricas
for col in ['city', 'country', 'torneio']:
    if col in df.columns:
        df[col] = df[col].fillna('UNKNOWN')
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

# 8. Criar diferenças entre stats de jogador 1 e 2
stat_pairs = [
    ('FH_Spin', 'FH_Spin_1', 'FH_Spin_2'),
    ('BH_Stab', 'BH_Stab_1', 'BH_Stab_2'),
    ('Fatigue', 'Fatigue_1', 'Fatigue_2'),
    ('Pressure', 'Pressure_1', 'Pressure_2'),
    ('shot_depth', 'shot_depth_1', 'shot_depth_2'),
    ('P1s', 'P1s_1', 'P1s_2'),
    ('P2s', 'P2s_1', 'P2s_2'),
    ('Prob_Retorno', 'Prob_Retorno_1', 'Prob_Retorno_2'),
    ('Ra', 'Ra_1', 'Ra_2'),
    ('Ef', 'Ef_1', 'Ef_2'),
    ('SGW', 'SGW_1', 'SGW_2'),
    ('RPW', 'RPW_1', 'RPW_2'),
    ('BP_Conversion', 'BP_Conversion_1', 'BP_Conversion_2'),
    ('Depth_Factor', 'Depth_Factor_1', 'Depth_Factor_2'),
]
for new_col, col1, col2 in stat_pairs:
    if col1 in df.columns and col2 in df.columns:
        df[f'diff_{new_col}'] = df[col1] - df[col2]

# 9. Remover colunas invariantes (só 1 valor ou tudo nulo)
for col in df.columns:
    if df[col].nunique(dropna=True) <= 1:
        print(f'Removendo coluna invariante: {col}')
        df.drop(col, axis=1, inplace=True)

# 10. Remover identificadores e dados pós-jogo das features
cols_remover = [
    'nome completo', 'jogador1', 'jogador2', 'id_partida', 'sets',
    'score_1', 'score_2', 'data', 'year of birth',
]
df_final = df.drop(cols_remover, axis=1, errors='ignore')

# 11. Salvar dataset pronto
df_final.to_csv('../data/processed_setkacup.csv', index=False)
print("Dataset processado salvo em ../data/processed_setkacup.csv")

# 12. Mostrar amostra das colunas finais
print(df_final.head())
