import joblib
from pathlib                import Path
from src.nlp.preprocessing  import preprocess_pipeline


MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODEL_PATH = MODELS_DIR / "mlp_intent_classifier.pkl"

try:
    model  = joblib.load(MODEL_PATH)
    print("Modelo MLP de intenção carregado com sucesso.")
    
except FileNotFoundError:
    print(f"Erro: Arquivo do modelo não encontrado em {MODEL_PATH}.")
    print("Por favor, execute o script 'src/mlp/train.py' primeiro.")
    model = None

def predict_intent(question: str) -> str:
   
    if model is None:
        return "ERRO: Modelo não carregado."
        
    processed_question  = preprocess_pipeline(question)
    prediction          = model.predict([processed_question])
    
    return prediction[0]