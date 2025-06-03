import requests

url = "https://www.thesportsdb.com/api/v1/json/1/all_leagues.php"
response = requests.get(url)

print("Status code:", response.status_code)
print("Conteúdo bruto da resposta:")
print(response.text[:500])  # Mostra os primeiros 500 caracteres

try:
    leagues = response.json().get('leagues', [])
    for league in leagues:
        if "Table Tennis" in league['strSport']:
            print(league['idLeague'], league['strLeague'])
except Exception as e:
    print("Erro ao processar JSON:", e)
