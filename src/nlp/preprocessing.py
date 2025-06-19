import re
import spacy
import string
import pandas as pd

from sklearn.pipeline                   import Pipeline
from sklearn.preprocessing              import FunctionTransformer
from sklearn.feature_extraction.text    import TfidfVectorizer

try:
    nlp = spacy.load("pt_core_news_sm")
    
except OSError:
    
    print("Modelo 'pt_core_news_sm' do spaCy não encontrado. Baixando...")
    
    from spacy.cli import download
    
    download("pt_core_news_sm")
    
    nlp = spacy.load("pt_core_news_sm")


def text_processing_func(series: pd.Series) -> pd.Series:
    
    series = series.astype(str)

    series = series.str.lower()
    
    series = series.str.replace(f'[{re.escape(string.punctuation)}]', '', regex=True)
    
    series = series.str.replace(r'\d+', '', regex=True)
    
    series = series.str.replace(r'\s+', ' ', regex=True).str.strip()

    processed_texts = []
    
    for doc in nlp.pipe(series, disable=["parser", "ner"]):
        
        lemmas = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        
        processed_texts.append(" ".join(lemmas))
    
    return pd.Series(processed_texts, index=series.index)


preprocess_pipeline = Pipeline([

    ('text_processing', FunctionTransformer(text_processing_func)),
    
    ('vectorizer', TfidfVectorizer(
        max_features    =1000,  
        ngram_range     =(1, 2)
    ))
])
