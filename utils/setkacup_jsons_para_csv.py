import os
import json
import pandas as pd

PASTA = "N:/Quantum_Pong/data/"
arquivos = sorted([arq for arq in os.listdir(PASTA) if arq.startswith("dados_setkacup_") and arq.endswith(".json")])

partidas = []
ids_partidas = set()

def processa_torneio(torneio, data_jogo):
    # Se o torneio for uma lista, processa cada um
    if isinstance(torneio, list):
        for t in torneio:
            processa_torneio(t, data_jogo)
        return
    torneio_nome = torneio.get('tournamentName', '')
    for match in torneio.get("matches", []):
        match_id = match.get("id")
        if match_id in ids_partidas:
            continue
        ids_partidas.add(match_id)
        try:
            p1 = match["player1"]["firstName"] + " " + match["player1"]["lastName"]
            p2 = match["player2"]["firstName"] + " " + match["player2"]["lastName"]
            p1_score = int(match.get("player1Score", "0"))
            p2_score = int(match.get("player2Score", "0"))
            sets = ", ".join([f"{s['p1Score']}-{s['p2Score']}" for s in match.get("setScores", [])])
            partidas.append({
                "data": data_jogo,
                "torneio": torneio_nome,
                "id_partida": match_id,
                "jogador_1": p1,
                "jogador_2": p2,
                "score_1": p1_score,
                "score_2": p2_score,
                "sets": sets
            })
        except Exception:
            continue

for arquivo in arquivos:
    with open(os.path.join(PASTA, arquivo), 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                torneios_lidos = json.loads(linha)
            except Exception as e:
                print(f"Erro ao ler linha em {arquivo}: {e}")
                continue
            data_jogo = arquivo.split("_")[-1].replace(".json", "")
            if isinstance(torneios_lidos, list):
                for torneio in torneios_lidos:
                    processa_torneio(torneio, data_jogo)
            else:
                processa_torneio(torneios_lidos, data_jogo)

df = pd.DataFrame(partidas)
if not df.empty:
    df = df.sort_values(by=["data", "id_partida"]).reset_index(drop=True)
    saida = os.path.join(PASTA, "setkacup_todas_partidas.csv")
    df.to_csv(saida, index=False, encoding="utf-8")
    print(f"\nCSV único pronto! Total de partidas: {len(df)}")
    print(f"Arquivo salvo em: {saida}")
else:
    print("Nenhuma partida processada. Verifique o formato dos arquivos JSON.")
