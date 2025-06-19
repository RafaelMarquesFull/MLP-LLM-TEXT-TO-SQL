import joblib
import pandas                as pd
import seaborn               as sns
import matplotlib.pyplot     as plt

from pathlib                 import Path
from sklearn.metrics         import classification_report, confusion_matrix
from sklearn.pipeline        import Pipeline
from sklearn.linear_model    import LogisticRegression
from sklearn.preprocessing   import LabelEncoder
from src.nlp.preprocessing   import preprocess_pipeline
from sklearn.model_selection import train_test_split, GridSearchCV


BASE_DIR    = Path(__file__).resolve().parent.parent.parent
DATA_DIR    = BASE_DIR / "data"
MODELS_DIR  = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODELS_DIR.mkdir(
    parents   =True, 
    exist_ok  =True
)
REPORTS_DIR.mkdir(
    parents   =True, 
    exist_ok  =True)

DATASET_PATH            = DATA_DIR / "raw" / "questions.csv"
PIPELINE_PATH           = MODELS_DIR / "intent_classification_pipeline.joblib"
LABEL_ENCODER_PATH      = MODELS_DIR / "intent_label_encoder.joblib"
CONFUSION_MATRIX_PATH   = REPORTS_DIR / "confusion_matrix.png"

def train_model():
   
    print(f"Carregando dataset de '{DATASET_PATH}'...")
    
    df  = pd.read_csv(DATASET_PATH)
    X   = df['question']
    y   = df['intent']

    print("\n--- Distribuição das Classes (Dataset Aumentado) ---")
    print(y.value_counts())
    print("-" * 30)
    print("\nCodificando os rótulos (intents)...")
    
    label_encoder   = LabelEncoder()
    y_encoded       = label_encoder.fit_transform(y)

    
    print("Dividindo o dataset em treino e teste...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, 
        test_size    =0.2, 
        random_state =42, 
        stratify     =y_encoded
    )

    
    pipeline = Pipeline([
        
        ('preprocessor', preprocess_pipeline),
        ('classifier', LogisticRegression(
            max_iter     =1000, 
            random_state =42
        ))
        
    ])

    
    param_grid = {
        
        'preprocessor__vectorizer__max_features' : [2000, 3000, 4000],
        'preprocessor__vectorizer__ngram_range'  : [(1, 1), (1, 2), (1, 3)],
        'preprocessor__vectorizer__min_df'       : [1, 2], 
        'classifier__C'                          : [0.1, 1, 10, 50],
        'classifier__solver'                     : ['liblinear', 'saga']
        
    }
    
    
    print("\nIniciando a busca refinada de hiperparâmetros para LogisticRegression...")
    
    grid_search = GridSearchCV(
        pipeline, 
        param_grid, 
        cv      =5, 
        n_jobs  =-1, 
        verbose =1, 
        scoring ='accuracy'
    )
    
    grid_search.fit(
        X_train, 
        y_train
    )

    
    print("\nBusca concluída!")
    print("-" * 30)
    print(f"Melhor modelo encontrado: {grid_search.best_estimator_.named_steps['classifier'].__class__.__name__}")
    print(f"Melhores parâmetros: {grid_search.best_params_}")
    
    best_model  = grid_search.best_estimator_
    y_pred      = best_model.predict(X_test)

    print("\n--- Relatório de Classificação ---")
    
    report      = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    
    print(report)
    print("-" * 30)
    
    print("Gerando a matriz de confusão visual...")
    
    cm          = confusion_matrix(y_test, y_pred)
    
    plt.figure(
        figsize =(10, 8)
    )
    sns.heatmap(
                cm, 
                annot       =True, 
                fmt         ='d', 
                cmap        ='Blues', 
                xticklabels =label_encoder.classes_, 
                yticklabels =label_encoder.classes_
            )
    plt.title('Matriz de Confusão do Melhor Modelo')
    plt.ylabel('Verdadeiro')
    plt.xlabel('Previsto')
    plt.savefig(CONFUSION_MATRIX_PATH)
    
    print(f"Matriz de confusão salva em: '{CONFUSION_MATRIX_PATH}'")
    print(f"\nSalvando o melhor pipeline encontrado em '{PIPELINE_PATH}'...")
    
    joblib.dump(best_model, PIPELINE_PATH)
    
    print(f"Salvando o codificador de rótulos em '{LABEL_ENCODER_PATH}'...")
    
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    print("\nTreinamento otimizado concluído com sucesso!")

if __name__ == '__main__':
    train_model()

