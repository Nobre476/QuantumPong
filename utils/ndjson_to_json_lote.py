import os
import json

# Pasta com os arquivos NDJSON/text originais
PASTA = "N:/Quantum_Pong/data/"

# Vai pegar todos arquivos .text ou .ndjson (ou ajuste para sua extensão)
arquivos = [f for f in os.listdir(PASTA) if f.endswith('.text') or f.endswith('.ndjson')]

for nome in arquivos:
    input_path = os.path.join(PASTA, nome)
    output_path = os.path.join(PASTA, nome.replace('.text', '.json').replace('.ndjson', '.json'))
    print(f"Convertendo: {input_path} -> {output_path}")
    lista = []
    with open(input_path, encoding='utf-8') as fin:
        for linha in fin:
            linha = linha.strip()
            if linha:
                try:
                    obj = json.loads(linha)
                    lista.append(obj)
                except Exception as e:
                    print(f"Erro ao converter uma linha em {nome}: {e}")
    with open(output_path, 'w', encoding='utf-8') as fout:
        json.dump(lista, fout, ensure_ascii=False, indent=2)
    print(f"Arquivo JSON pronto: {output_path} ({len(lista)} objetos)\n")

print("Todos os arquivos foram convertidos!")
