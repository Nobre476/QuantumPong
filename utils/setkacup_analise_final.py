import requests
import json
import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time
import glob

# Diretórios de saída na pasta especificada:
BASE_DATA_DIR = r"N:\Quantum_Pong\data"
PASTA_MATCHES = os.path.join(BASE_DATA_DIR, "dados_setkacup")
PASTA_JOGADORES = os.path.join(BASE_DATA_DIR, "jogadores_setkacup")
CSV_SAIDA = os.path.join(BASE_DATA_DIR, "integrado_setkacup.csv")
SQLITE_SAIDA = os.path.join(BASE_DATA_DIR, "integrado_setkacup.sqlite")

# Garante que as pastas existem
os.makedirs(PASTA_MATCHES, exist_ok=True)
os.makedirs(PASTA_JOGADORES, exist_ok=True)
DIAS_HISTORICO = 90  # 3 meses

def baixar_todos_jogadores(num_paginas=202, count=50):
    todos = []
    for page in range(1, num_paginas + 1):
        url = f"https://tabletennis.setkacup.com/api/Players/en/paged?gender=-1&count={count}&page={page}"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json().get("items", [])
            if not data:
                break
            todos.extend(data)
        else:
            break
    with open(os.path.join(PASTA_JOGADORES, "todos_jogadores.json"), "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    return todos

def baixar_partidas(datas, periodos=7):
    base_url = "https://tabletennis.setkacup.com/api/Tournaments/en"
    for data in datas:
        for periodo in range(1, periodos+1):
            arq_destino = os.path.join(PASTA_MATCHES, f"{data}_periodo{periodo}.json")
            if os.path.exists(arq_destino):
                continue
            url = f"{base_url}?date={data}&dayPeriod={periodo}"
            r = requests.get(url)
            if r.status_code == 200 and r.content.strip() not in [b'[]', b'null']:
                with open(arq_destino, 'w', encoding='utf-8') as f:
                    json.dump(r.json(), f, ensure_ascii=False, indent=2)

def remover_antigos():
    arquivos = glob.glob(os.path.join(PASTA_MATCHES, "*_periodo*.json"))
    datas = set()
    for arq in arquivos:
        nome = os.path.basename(arq)
        try:
            data = nome.split('_')[0]
            data_dt = datetime.strptime(data, "%Y-%m-%d")
            datas.add(data_dt)
        except:
            continue
    if not datas:
        return
    datas_ordenadas = sorted(datas)
    if len(datas_ordenadas) > DIAS_HISTORICO:
        datas_apagar = datas_ordenadas[:-DIAS_HISTORICO]
        for data in datas_apagar:
            padrao = os.path.join(PASTA_MATCHES, f"{data.strftime('%Y-%m-%d')}_periodo*.json")
            for arq in glob.glob(padrao):
                print(f"Removendo arquivo antigo: {arq}")
                os.remove(arq)

# --------- Funções de Métricas (iguais à versão anterior, omitidas aqui por espaço)
def safe_div(x, y, default=0):
    try:
        return float(x)/float(y) if y else default
    except:
        return default

def calc_fh_spin(rank_setka, rank_uttf, torneios, ano_nasc, score1, score2, sets, ano_atual):
    try:
        base = (rank_setka/50 + rank_uttf/50)
        tor_mult = 1 + torneios/100
        age_mult = 1.3 - 0.01 * (ano_atual - ano_nasc)
        set_diff = safe_div((score1-score2), sets)
        fh = base * tor_mult * age_mult + set_diff
        fh_norm = (fh/10)*100
        return fh, min(max(fh_norm,0),100)
    except:
        return 0,0

def calc_bh_stab(rank_setka, rank_uttf, torneios, ano_nasc, score1, score2, sets, ano_atual):
    try:
        base = (rank_setka/30 + rank_uttf/70)
        tor_mult = 1 + 0.5*torneios/50
        age_mult = 0.7 + 0.01*(ano_atual - ano_nasc)
        close_loss_pen = abs(score1-score2)/10
        bh = base * tor_mult * age_mult - close_loss_pen
        bh_norm = (bh/8)*100
        return bh, min(max(bh_norm,0),100)
    except:
        return 0,0

def calc_fatigue(torneios, total_sets, ano_nasc, ano_atual):
    try:
        base = torneios/2 + total_sets/5
        age_mult = 1 + 0.02*(ano_atual - ano_nasc)
        fat = base * age_mult
        fat_norm = (fat/50)*100
        return fat, min(max(fat_norm,0),100)
    except:
        return 0,0

def calc_pressure(rank_uttf, derrotas_recentes, ano_nasc, ano_atual):
    try:
        comp = (100-rank_uttf)/10
        loss = derrotas_recentes*2/5
        age = (40-(ano_atual-ano_nasc))/10
        press = comp + loss + age
        press_norm = (press/20)*100
        return press, min(max(press_norm,0),100)
    except:
        return 0,0

def calc_rally_length(rank1, rank2, birth1, birth2, ano_atual, surface_factor=1.0):
    idade1 = ano_atual - birth1 if birth1 else 28
    idade2 = ano_atual - birth2 if birth2 else 28
    idade_media = (idade1 + idade2) / 2
    media_rank = (rank1 + rank2) / 2
    rally_length = media_rank * (1 + idade_media/100) * surface_factor
    rally_norm = min(max(rally_length / 400 * 100, 0), 100)
    return rally_length, rally_norm

def calc_shot_depth(rank, birth, ano_atual):
    idade = ano_atual - birth if birth else 28
    ajuste_idade = 0
    if idade < 25:
        ajuste_idade = 0.05
    elif idade > 30:
        ajuste_idade = -0.05
    shot_depth = 0.8 - (rank/1000) + ajuste_idade
    shot_depth_percent = min(max(shot_depth, 0), 1) * 100
    return shot_depth, shot_depth_percent

def calc_p1s(rank_uttf):
    p1s = max(0, 0.75 - 0.005 * rank_uttf)
    return min(p1s, 1)

def calc_p2s(p1s):
    return min(p1s + 0.1, 1.0)

def calc_prob_retorno(shot_depth):
    return max(0, min(0.6 - 0.2 * shot_depth, 1))

def calc_ra(rank_setka_opp, rank_setka_self):
    if rank_setka_self == 0:
        return 1
    ra = 0.3 + 0.2 * (rank_setka_opp / rank_setka_self)
    return max(0, min(ra, 1))

def calc_ef(rally_length):
    ef = 0.1 + 0.02 * rally_length
    return max(0, min(ef, 1))

def calc_sgw(P1s, Prob_Retorno_op, Ra, Ef):
    try:
        return ((P1s + (1 - Prob_Retorno_op)) / (Ra if Ra else 1)) * Ef
    except:
        return 0

def calc_rpw(P1s_op, Prob_Retorno, BH_Stab_norm, FH_Spin_norm):
    try:
        return (1 - P1s_op) * Prob_Retorno * (1 + (BH_Stab_norm + FH_Spin_norm)/2)
    except:
        return 0

def calc_bp_conversion(Pressure_norm, RPW, Fatigue_norm_op):
    try:
        if Fatigue_norm_op == 0: return 0
        val = (Pressure_norm * RPW) / Fatigue_norm_op
        if Pressure_norm > 0.7:
            val *= 0.9
        return val
    except:
        return 0

def calc_depth_factor(shot_depth_percent, FH_Spin_norm, BH_Stab_norm, rally_length_norm):
    try:
        if rally_length_norm == 0: return 0
        return (shot_depth_percent * (FH_Spin_norm + BH_Stab_norm)) / rally_length_norm
    except:
        return 0

def processar_dados():
    ano_atual = datetime.now().year
    with open(os.path.join(PASTA_JOGADORES, "todos_jogadores.json"), encoding='utf-8') as f:
        jogadores = json.load(f)
    d_jog = {j["id"]: j for j in jogadores}
    linhas = []
    for arq in os.listdir(PASTA_MATCHES):
        if not arq.endswith(".json"):
            continue
        with open(os.path.join(PASTA_MATCHES, arq), encoding='utf-8') as f:
            try:
                torneios = json.load(f)
            except:
                continue
        for torneio in torneios:
            torneio_nome = torneio.get("token") or torneio.get("tournamentName")
            data = torneio.get("startDate", "")[:10]
            matches = torneio.get("matches", [])
            surface_factor = 1.0
            for match in matches:
                p1 = match.get("player1", {})
                p2 = match.get("player2", {})
                id1 = p1.get("id")
                id2 = p2.get("id")
                jogador1 = d_jog.get(id1, {})
                jogador2 = d_jog.get(id2, {})
                sets = match.get("setScores", [])
                sets_str = json.dumps([[s.get("p1Score", 0), s.get("p2Score", 0)] for s in sets])
                sets_cnt = len(sets)
                score1 = safe_div(match.get("player1Score", 0), 1)
                score2 = safe_div(match.get("player2Score", 0), 1)
                def extrair(jogador):
                    rank_setka = safe_div(jogador.get("rating",0),1)
                    rank_uttf = safe_div(jogador.get("uttfRating",0),1)
                    torneios = safe_div(jogador.get("tournamentsPlayed",0),1)
                    city = jogador.get("city","")
                    country = jogador.get("country","")
                    year_of_birth = safe_div(jogador.get("yearOfBirth",ano_atual-25),1)
                    defeats = safe_div(jogador.get("recentLose",0),1)
                    return rank_setka, rank_uttf, torneios, city, country, year_of_birth, defeats
                # Dados jogadores
                r1, u1, t1, c1, pa1, yb1, d1 = extrair(jogador1)
                r2, u2, t2, c2, pa2, yb2, d2 = extrair(jogador2)
                # Métricas Jogador1
                fh1, fh1_norm = calc_fh_spin(r1, u1, t1, yb1, score1, score2, sets_cnt, ano_atual)
                bh1, bh1_norm = calc_bh_stab(r1, u1, t1, yb1, score1, score2, sets_cnt, ano_atual)
                fat1, fat1_norm = calc_fatigue(t1, sets_cnt, yb1, ano_atual)
                press1, press1_norm = calc_pressure(u1, d1, yb1, ano_atual)
                sd1, sd1_percent = calc_shot_depth(r1, yb1, ano_atual)
                # Métricas Jogador2
                fh2, fh2_norm = calc_fh_spin(r2, u2, t2, yb2, score2, score1, sets_cnt, ano_atual)
                bh2, bh2_norm = calc_bh_stab(r2, u2, t2, yb2, score2, score1, sets_cnt, ano_atual)
                fat2, fat2_norm = calc_fatigue(t2, sets_cnt, yb2, ano_atual)
                press2, press2_norm = calc_pressure(u2, d2, yb2, ano_atual)
                sd2, sd2_percent = calc_shot_depth(r2, yb2, ano_atual)
                # Métricas da partida
                rally, rally_norm = calc_rally_length(r1, r2, yb1, yb2, ano_atual, surface_factor)
                P1s_1 = calc_p1s(u1)
                P2s_1 = calc_p2s(P1s_1)
                Prob_Retorno_1 = calc_prob_retorno(sd1)
                Ra_1 = calc_ra(r2, r1)
                Ef_1 = calc_ef(rally)
                P1s_2 = calc_p1s(u2)
                P2s_2 = calc_p2s(P1s_2)
                Prob_Retorno_2 = calc_prob_retorno(sd2)
                Ra_2 = calc_ra(r1, r2)
                Ef_2 = calc_ef(rally)
                SGW_1 = calc_sgw(P1s_1, Prob_Retorno_2, Ra_1, Ef_1)
                SGW_2 = calc_sgw(P1s_2, Prob_Retorno_1, Ra_2, Ef_2)
                soma_SGW = SGW_1 + SGW_2 if (SGW_1 + SGW_2) else 1
                SGW_1_norm = SGW_1 / soma_SGW
                SGW_2_norm = SGW_2 / soma_SGW
                RPW_1 = calc_rpw(P1s_2, Prob_Retorno_1, bh1_norm, fh1_norm)
                RPW_2 = calc_rpw(P1s_1, Prob_Retorno_2, bh2_norm, fh2_norm)
                soma_RPW = RPW_1 + RPW_2 if (RPW_1 + RPW_2) else 1
                RPW_1_norm = RPW_1 / soma_RPW
                RPW_2_norm = RPW_2 / soma_RPW
                BP_Conversion_1 = calc_bp_conversion(press1_norm, RPW_1, fat2_norm)
                BP_Conversion_2 = calc_bp_conversion(press2_norm, RPW_2, fat1_norm)
                Depth_Factor_1 = calc_depth_factor(sd1_percent/100, fh1_norm, bh1_norm, rally_norm)
                Depth_Factor_2 = calc_depth_factor(sd2_percent/100, fh2_norm, bh2_norm, rally_norm)
                linha = [
                    f'{p1.get("firstName","")} {p1.get("lastName","")}',
                    r1, u1, t1, c1, pa1, yb1,
                    data, torneio_nome, match.get("id", ""),
                    f'{p1.get("firstName","")} {p1.get("lastName","")}',
                    f'{p2.get("firstName","")} {p2.get("lastName","")}',
                    match.get("player1Score", ""), match.get("player2Score", ""), sets_str,
                    fh1, fh1_norm, bh1, bh1_norm, fat1, fat1_norm, press1, press1_norm,
                    fh2, fh2_norm, bh2, bh2_norm, fat2, fat2_norm, press2, press2_norm,
                    rally, rally_norm, sd1, sd1_percent, sd2, sd2_percent,
                    P1s_1, P2s_1, Prob_Retorno_1, Ra_1, Ef_1,
                    P1s_2, P2s_2, Prob_Retorno_2, Ra_2, Ef_2,
                    SGW_1, SGW_1_norm, RPW_1, RPW_1_norm, BP_Conversion_1, Depth_Factor_1,
                    SGW_2, SGW_2_norm, RPW_2, RPW_2_norm, BP_Conversion_2, Depth_Factor_2
                ]
                if not any(l[9] == linha[9] for l in linhas):
                    linhas.append(linha)
    return linhas

def salvar_csv_sqlite(linhas):
    colunas = [
        "nome completo", "rank setka cup", "rank uttf", "tournaments", "city", "country", "year of birth",
        "data", "torneio", "id_partida", "jogador1", "jogador2", "score_1", "score_2", "sets",
        "FH_Spin_1", "FH_Spin_norm_1", "BH_Stab_1", "BH_Stab_norm_1", "Fatigue_1", "Fatigue_norm_1", "Pressure_1", "Pressure_norm_1",
        "FH_Spin_2", "FH_Spin_norm_2", "BH_Stab_2", "BH_Stab_norm_2", "Fatigue_2", "Fatigue_norm_2", "Pressure_2", "Pressure_norm_2",
        "rally_length", "rally_length_norm",
        "shot_depth_1", "shot_depth_1_percent", "shot_depth_2", "shot_depth_2_percent",
        "P1s_1", "P2s_1", "Prob_Retorno_1", "Ra_1", "Ef_1",
        "P1s_2", "P2s_2", "Prob_Retorno_2", "Ra_2", "Ef_2",
        "SGW_1", "SGW_1_norm", "RPW_1", "RPW_1_norm", "BP_Conversion_1", "Depth_Factor_1",
        "SGW_2", "SGW_2_norm", "RPW_2", "RPW_2_norm", "BP_Conversion_2", "Depth_Factor_2"
    ]
    df = pd.DataFrame(linhas, columns=colunas)
    df.to_csv(CSV_SAIDA, index=False, encoding="utf-8")
    conn = sqlite3.connect(SQLITE_SAIDA)
    df.to_sql("partidas", conn, if_exists="replace", index=False)
    conn.close()
    print(f"CSV e SQLite atualizados. Linhas: {len(df)}")

def main():
    print("Iniciando coleta automática SetkaCup.")
    while True:
        print(f"[{datetime.now()}] Atualizando base de jogadores...")
        baixar_todos_jogadores(num_paginas=202, count=50)
        datas = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(DIAS_HISTORICO-1, -1, -1)]
        print(f"[{datetime.now()}] Atualizando partidas dos últimos {DIAS_HISTORICO} dias...")
        baixar_partidas(datas, periodos=7)
        remover_antigos()
        print(f"[{datetime.now()}] Processando e salvando integrados...")
        linhas = processar_dados()
        salvar_csv_sqlite(linhas)
        print(f"[{datetime.now()}] Atualização completa! Aguardando 3 horas para próxima execução...\n")
        time.sleep(3 * 60 * 60)

if __name__ == "__main__":
    main()
