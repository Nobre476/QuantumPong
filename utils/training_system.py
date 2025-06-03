# N:/Quantum_Pong/utils/training_system.py
import random
import math
# Mantém o import original mas configura o ambiente primeiro
from utils.qi_calculator import calculate_qi

class TrainingDrill:
    """Classe que simula exercícios de treino de tênis de mesa"""
    
    def __init__(self, difficulty=1.0):
        """Inicializa o treino com uma dificuldade padrão"""
        self.difficulty = difficulty  # 1.0 = normal, 1.5 = difícil, etc.
        self.completed = False       # Marca se o treino foi finalizado

    def forehand_drill(self, attempts=10):
        """Simula um treino de forehand (rebater com o lado dominante)"""
        scores = []
        for _ in range(attempts):
            base_score = random.uniform(0.7, 0.9)  # Performance base
            adjusted_score = base_score * (1 - (self.difficulty * 0.1))
            scores.append(adjusted_score)
        return sum(scores) / len(scores)

    def backhand_drill(self, attempts=10):
        """Simula um treino de backhand (rebater com o lado não-dominante)"""
        scores = []
        for _ in range(attempts):
            base_score = random.uniform(0.6, 0.85)  # Backhand é menos preciso
            adjusted_score = base_score * (1 - (self.difficulty * 0.15))
            scores.append(adjusted_score)
        return sum(scores) / len(scores)


def simulate_training_session(difficulty=1.0, duration=30):
    """
    Simula uma sessão completa de treino e retorna:
    - Melhorias técnicas
    - Fadiga acumulada
    """
    drill = TrainingDrill(difficulty)
    
    # Executa os exercícios
    fh_improvement = drill.forehand_drill()
    bh_improvement = drill.backhand_drill()
    
    # Calcula fadiga (limita a 100%)
    fatigue = min(1.0, (duration * difficulty) / 45)
    
    return {
        "forehand_improvement": fh_improvement,
        "backhand_improvement": bh_improvement,
        "fatigue_generated": fatigue
    }


# ==============================================
# Bloco de testes (opcional - só roda se executar este arquivo diretamente)
# ==============================================
if __name__ == "__main__":
    print("=== TESTE DA CLASSE TrainingDrill ===")
    
    # Teste 1: Treino normal
    normal_session = simulate_training_session(difficulty=1.0, duration=30)
    print("\n🔵 Treino Normal (Dificuldade 1.0, 30min):")
    print(f"Forehand: {normal_session['forehand_improvement']:.2f}")
    print(f"Backhand: {normal_session['backhand_improvement']:.2f}")
    print(f"Fadiga: {normal_session['fatigue_generated']:.2f}")

    # Teste 2: Treino intenso
    hard_session = simulate_training_session(difficulty=1.5, duration=45)
    print("\n🔴 Treino Difícil (Dificuldade 1.5, 45min):")
    print(f"Forehand: {hard_session['forehand_improvement']:.2f}")
    print(f"Backhand: {hard_session['backhand_improvement']:.2f}")
    print(f"Fadiga: {hard_session['fatigue_generated']:.2f}")