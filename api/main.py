import sys
from pathlib import Path

# Adiciona o caminho da pasta principal ao Python
sys.path.append(str(Path(__file__).parent.parent))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quantum Pong API")

# Configuração CORS (permite frontend acessar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def status():
    return {"status": "API Online", "version": "5.0"}

@app.get("/qi/")
def calculate_qi(
    forehand_spin: float = 8,
    backhand_stability: float = 6,
    fatigue: float = 3,
    pressure: float = 4
):
    """Calcula o Qi Index (versão simplificada)"""
    numerator = 0.7 * forehand_spin + 0.3 * backhand_stability
    denominator = (fatigue**2 + 0.5 * pressure**2)**0.5
    qi = numerator / denominator if denominator != 0 else 0
    
    return {
        "qi_index": round(qi, 2),
        "flow_state": qi > 1.15,
        "message": "FLOW ATIVADO!" if qi > 1.15 else "Treine mais!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/qi-score/")
async def get_qi_score(fh_spin: float, bh_stability: float, fatigue: float, pressure: float):
    qi = (0.7*fh_spin + 0.3*bh_stability) / (fatigue + 0.5*pressure)
    return {"qi_index": qi, "flow_state": qi > 1.15}

from utils.racket_physics import calculate_rebound

@app.get("/rebound-angle/")
async def get_rebound_angle(incoming_angle: float, rubber_hardness: float = 45):
    return {"rebound_angle": calculate_rebound(incoming_angle, rubber_hardness)}