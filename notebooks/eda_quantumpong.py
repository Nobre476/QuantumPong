import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Carregar os dados
df = pd.read_csv('../data/integrado_setkacup.csv')

# 2. Converter colunas para número
numericas = [
    'score_1', 'score_2', 'rank setka cup', 'rank uttf', 'tournaments',
    'year of birth', 'FH_Spin_1', 'FH_Spin_norm_1', 'BH_Stab_1', 'BH_Stab_norm_1',
    'Fatigue_1', 'Fatigue_norm_1', 'Pressure_1', 'Pressure_norm_1',
    'FH_Spin_2', 'FH_Spin_norm_2', 'BH_Stab_2', 'BH_Stab_norm_2',
    'Fatigue_2', 'Fatigue_norm_2', 'Pressure_2', 'Pressure_norm_2',
    'rally_length', 'rally_length_norm', 'shot_depth_1', 'shot_depth_1_percent',
    'shot_depth_2', 'shot_depth_2_percent', 'P1s_1', 'P2s_1', 'Prob_Retorno_1',
    'Ra_1', 'Ef_1', 'P1s_2', 'P2s_2', 'Prob_Retorno_2', 'Ra_2', 'Ef_2',
    'SGW_1', 'SGW_1_norm', 'RPW_1', 'RPW_1_norm', 'BP_Conversion_1', 'Depth_Factor_1',
    'SGW_2', 'SGW_2_norm', 'RPW_2', 'RPW_2_norm', 'BP_Conversion_2', 'Depth_Factor_2'
]

for col in numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Visualizar primeiras linhas e tipos de dados
print("Primeiras linhas:")
print(df.head())
print("\nTipos de dados:")
print(df.info())

# 4. Checar valores faltantes e únicos
print('\nValores faltantes por coluna:')
print(df.isnull().sum())
print('\nValores únicos por coluna:')
print(df.nunique())

# 5. Estatísticas descritivas
print('\nEstatísticas descritivas:')
print(df.describe())

# 6. Criar targets auxiliares para análise
df['target_vencedor'] = (df['score_1'] > df['score_2']).astype(int)
df['total_pontos'] = df['score_1'] + df['score_2']
df['target_over_79_5'] = (df['total_pontos'] > 79.5).astype(int)

print('\nBalanceamento VENCEDOR:')
print(df['target_vencedor'].value_counts(normalize=True))
print('\nBalanceamento OVER 79.5:')
print(df['target_over_79_5'].value_counts(normalize=True))

# 7. Histogramas de variáveis importantes
cols_hist = [
    'score_1','score_2','rank setka cup','rank uttf','tournaments',
    'FH_Spin_1','FH_Spin_2','total_pontos'
]
for col in cols_hist:
    if col in df.columns:
        plt.figure(figsize=(6,2))
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f'Histograma: {col}')
        plt.tight_layout()
        plt.savefig(f"{col}_hist.png")
        plt.show()

# 8. Boxplot dos scores por vencedor
plt.figure(figsize=(5,3))
sns.boxplot(x='target_vencedor', y='score_1', data=df)
plt.title('Score 1 por Vencedor')
plt.tight_layout()
plt.savefig("score1_por_vencedor.png")
plt.show()

# 9. Matriz de correlação entre variáveis numéricas
plt.figure(figsize=(14,8))
corr = df.select_dtypes(include=np.number).corr()
sns.heatmap(corr, cmap='coolwarm', annot=False)
plt.title('Matriz de Correlação')
plt.tight_layout()
plt.savefig("correlacao.png")
plt.show()

# 10. Diferença de rank dos jogadores por vencedor
if 'rank setka cup' in df.columns and 'rank uttf' in df.columns:
    df['diff_rank'] = df['rank setka cup'] - df['rank uttf']
    plt.figure(figsize=(6,3))
    sns.violinplot(x='target_vencedor', y='diff_rank', data=df)
    plt.title('Diferença de Rank por Vencedor')
    plt.tight_layout()
    plt.savefig("diff_rank_por_vencedor.png")
    plt.show()

# 11. Top valores em variáveis categóricas
for col in ['city','country','torneio']:
    if col in df.columns:
        print(f'\nTop valores de {col}:')
        print(df[col].value_counts().head(10))

# 12. Outliers (boxplot)
cols_box = ['score_1','score_2','FH_Spin_1','FH_Spin_2','Fatigue_1','Fatigue_2']
for col in cols_box:
    if col in df.columns:
        plt.figure(figsize=(6,2))
        sns.boxplot(x=df[col])
        plt.title(f'Boxplot: {col}')
        plt.tight_layout()
        plt.savefig(f"{col}_boxplot.png")
        plt.show()

# 13. Exemplo: salvar dados filtrados (opcional)
df_filtrado = df[df['score_1'] > 50]
df_filtrado.to_csv("jogos_score1_maior_50.csv", index=False)
print("\nJogos com score_1 > 50 salvos em jogos_score1_maior_50.csv")
