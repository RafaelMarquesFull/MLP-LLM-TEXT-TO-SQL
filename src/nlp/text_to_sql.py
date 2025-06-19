
from src.mlp.predict    import predict_intent
from src.llm.generator  import generate_sql_query

def process_question_to_sql(question: str) -> dict:
   
    intent    = predict_intent(question)
    
    entities  = []

    sql_query = generate_sql_query(question, intent, entities)
    
    return {
        "original_question" : question,
        "predicted_intent"  : intent,
        "generated_sql"     : sql_query
    }