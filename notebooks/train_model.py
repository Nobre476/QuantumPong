import os
import warnings
import signal
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from tpot import TPOTClassifier
import optuna
import joblib

# Configurações iniciais
warnings.filterwarnings('ignore', category=UserWarning)
os.environ['DASK_DISTRIBUTED__WORKER__DAEMON'] = 'False'

# Funções auxiliares
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operação excedeu o tempo limite!")

def set_timeout(seconds):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)

def clear_timeout():
    signal.alarm(0)

# Diretórios
SAVE_DIR = r'N:\Quantum_Pong\models'
os.makedirs(SAVE_DIR, exist_ok=True)
CHECKPOINT = os.path.join(SAVE_DIR, 'tpot_checkpoints')
OPTUNA_DB = os.path.join(SAVE_DIR, 'quantumpong_optuna.db')

def load_and_prepare_data():
    """Carrega e prepara os dados para modelagem"""
    print("\n=== CARREGANDO E PREPARANDO DADOS ===")
    
    # Carregar dados
    df = pd.read_csv(r'N:\Quantum_Pong\data\integrado_setkacup.csv')
    
    # Converter colunas para numérico
    df['score_1'] = pd.to_numeric(df['score_1'], errors='coerce')
    df['score_2'] = pd.to_numeric(df['score_2'], errors='coerce')
    df['total_pontos'] = df['score_1'] + df['score_2']
    
    # Selecionar features e target
    features_candidatas = [
        'FH_Spin_1', 'FH_Spin_norm_1', 'BH_Stab_1', 'Fatigue_1', 'Fatigue_norm_1',
        'FH_Spin_2', 'FH_Spin_norm_2', 'BH_Stab_2', 'Fatigue_2', 'Fatigue_norm_2',
        'RPW_1', 'RPW_1_norm', 'BP_Conversion_1', 'RPW_2', 'RPW_2_norm', 'BP_Conversion_2'
    ]
    
    features = [col for col in features_candidatas if col in df.columns]
    df_clean = df.dropna(subset=features + ['score_1', 'score_2']).copy()  # <- .copy() adicionado
    
    # Definir threshold
    best_threshold = np.percentile(df_clean['total_pontos'], 50)
    df_clean['target'] = (df_clean['total_pontos'] > best_threshold).astype(int)
    
    print(f"Dados carregados: {len(df_clean)} linhas válidas")
    print(f"Threshold usado: {best_threshold:.1f}")
    print(f"Features utilizadas: {len(features)}")
    
    return df_clean, features, 'target'

def run_optuna(X_train, y_train, X_test, y_test):
    """Otimização de hiperparâmetros com Optuna"""
    print("\n=== OTIMIZAÇÃO COM OPTUNA ===")
    
    study = optuna.create_study(
        study_name='quantumpong_study',
        direction="maximize",
        storage=f"sqlite:///{OPTUNA_DB}",
        load_if_exists=True
    )

    def objective(trial):
        n_estimators = trial.suggest_int("n_estimators", 100, 400)
        max_depth = trial.suggest_int("max_depth", 4, 20)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 10)
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            class_weight="balanced",
            random_state=42
        )
        score = cross_val_score(clf, X_train, y_train, cv=5, scoring='accuracy').mean()
        return score

    study.optimize(objective, n_trials=25)
    print('\n[Optuna] Melhores parâmetros:', study.best_params)
    print('[Optuna] Melhor acurácia validação:', study.best_value)

    clf = RandomForestClassifier(**study.best_params, class_weight="balanced", random_state=42)
    clf.fit(X_train, y_train)
    optuna_test_acc = clf.score(X_test, y_test)
    print(f'[Optuna] Acurácia no teste: {optuna_test_acc}')
    
    return clf, optuna_test_acc

def run_tpot(X_train, y_train, X_test, y_test):
    """Otimização de pipeline com TPOT"""
    print("\n=== OTIMIZAÇÃO COM TPOT ===")
    
    try:
        tpot = TPOTClassifier(
            generations=5,
            population_size=20,
            periodic_checkpoint_folder=CHECKPOINT,
            max_time_mins=20,
            random_state=42,
            n_jobs=1
        )
        
        if hasattr(signal, 'SIGALRM'):
            set_timeout(1200)  # 20 minutos de timeout
            
        tpot.fit(X_train, y_train)
        
        if hasattr(signal, 'SIGALRM'):
            clear_timeout()
            
        tpot_pipeline = tpot.fitted_pipeline_
        tpot_test_acc = tpot_pipeline.score(X_test, y_test)
        print(f'[TPOT] Score no teste: {tpot_test_acc}')
        
        return tpot_pipeline, tpot_test_acc
        
    except Exception as e:
        print(f"Erro no TPOT: {str(e)}")
        return None, None

def run_simple_models(X_train, y_train, X_test, y_test):
    """Executa modelos simples para comparação"""
    print("\n=== MODELOS SIMPLES ===")
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    print(f"Random Forest - Acurácia: {rf_accuracy:.4f}")
    
    # Logistic Regression
    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_accuracy = accuracy_score(y_test, lr_pred)
    print(f"Logistic Regression - Acurácia: {lr_accuracy:.4f}")
    
    return rf, lr, rf_accuracy, lr_accuracy

def main():
    try:
        # Carregar e preparar dados
        df, features, target = load_and_prepare_data()
        X = df[features]
        y = df[target]
        
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalização
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modelos simples
        rf, lr, rf_acc, lr_acc = run_simple_models(X_train_scaled, y_train, X_test_scaled, y_test)
        
        # Optuna
        optuna_model, optuna_acc = run_optuna(X_train_scaled, y_train, X_test_scaled, y_test)
        joblib.dump({'model': optuna_model, 'scaler': scaler}, 
                   os.path.join(SAVE_DIR, 'best_rf_optuna.joblib'))
        
        # TPOT
        tpot_model, tpot_acc = run_tpot(X_train_scaled, y_train, X_test_scaled, y_test)
        if tpot_model:
            joblib.dump({'model': tpot_model, 'scaler': scaler}, 
                       os.path.join(SAVE_DIR, 'best_tpot.joblib'))
            # Exporta pipeline
            try:
                # Exporta para python apenas se método existir
                from tpot.export_utils import export_pipeline
                export_pipeline(tpot_model, os.path.join(SAVE_DIR, 'best_pipeline_tpot.py'))
            except Exception:
                pass
        
        # Resumo final
        print('\n========== RESUMO FINAL ==========')
        print(f'[Modelos Simples] Random Forest: {rf_acc:.4f}')
        print(f'[Modelos Simples] Logistic Regression: {lr_acc:.4f}')
        print(f'[Optuna] Test Accuracy: {optuna_acc:.4f}')
        print(f'[TPOT] Test Accuracy: {tpot_acc:.4f}' if tpot_acc is not None else "[TPOT] Test Accuracy: N/A")
        print('\nModelos salvos na pasta:', SAVE_DIR)
        
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário")
    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
