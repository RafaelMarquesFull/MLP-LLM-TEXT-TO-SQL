import os
import pandas as pd
import sqlite3
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH      = PROJECT_ROOT / "data" / "automobiles.db"

def get_db_schema_and_values(db_path: Path) -> str:

    if not db_path.exists():
        return "ERRO: Arquivo do banco de dados não encontrado."
    
    try:
        with sqlite3.connect(db_path) as conn:
            
            cursor = conn.cursor()
           
            cursor.execute("PRAGMA table_info(automobiles);")
            
            columns = cursor.fetchall()
            
            if not columns:
                return "ERRO: Nenhuma tabela 'automobiles' encontrada no banco."

            schema_str     = "Tabela 'automobiles' com as seguintes colunas:\n"
            column_names   = []
            
            for col in columns:
                
                schema_str += f"- {col[1]} (tipo: {col[2]})\n"
                column_names.append(col[1])
                

            value_examples_str  = "\n### Exemplos de Valores em Colunas Importantes:\n"
            cols_to_sample      = ['body-style', 'transmission', 'fuel-type', 'drive-wheels']
            
            for col_name in cols_to_sample:
                
                if col_name in column_names:
                    
                    cursor.execute(f'SELECT DISTINCT "{col_name}" FROM automobiles')
                    values              = [row[0] for row in cursor.fetchall()]
                    value_examples_str += f"- Valores possíveis para a coluna \"{col_name}\": {values}\n"

            return schema_str + value_examples_str
            
    except Exception as e:
        return f"ERRO ao ler o schema do banco de dados: {e}"


def generate_sql_query(question: str, intent: str) -> str:
   
    db_context = get_db_schema_and_values(DB_PATH)
    
    if "ERRO" in db_context:
        return f"SELECT '{db_context}';"
    
    prompt = f"""
        Você é um assistente especialista em SQLite. Sua tarefa é converter uma pergunta em uma consulta SQL precisa, usando três fontes de informação: a pergunta do usuário, a intenção geral (classificada por um modelo MLP) e o contexto detalhado do banco de dados.

        ### Contexto do Banco de Dados (Schema e Valores de Exemplo):
        {db_context}

        ### Intenção Principal (classificada pelo MLP):
        A intenção geral desta pergunta foi classificada como: **{intent}**.
        Use esta intenção como guia principal. Por exemplo, se a intenção for 'count_cars' ou 'GROUP_COUNT', sua consulta deve usar `COUNT(*)`.

        ### Instruções Cruciais:
        1.  Use os nomes de coluna e os valores EXATOS fornecidos na seção "Contexto do Banco de Dados".
        2.  A consulta deve responder à pergunta completa do usuário. Use a cláusula 'WHERE' com 'AND' para filtrar por todas as condições mencionadas na pergunta.
        3.  Gere APENAS a consulta SQL. Não inclua explicações ou comentários.
        4.  Se uma coluna tiver um hífen (ex: 'body-style'), coloque-a entre aspas duplas ("body-style").

        ### Pergunta Completa do Usuário:
        "{question}"

        ### Consulta SQL:
    """
    
    try:
        response = client.chat.completions.create(
            model="llama3.2-vision:11b-turbo", 
            messages=[
                {"role": "system", "content": "Você é um especialista em gerar consultas SQLite guiado por um classificador de intenção e um schema de banco de dados."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0,
            max_tokens  = 300
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
            
        return sql_query
    
    except Exception as e:
        return f"SELECT 'ERRO ao chamar a API da OpenAI: {e}';"


def generate_natural_language_response(question: str, db_result: pd.DataFrame | str) -> str:
    
    prompt = f"""
        Sua tarefa é responder à pergunta original de um usuário de forma amigável e direta, com base nos dados que foram retornados de uma consulta ao banco de dados.

        ### Pergunta Original do Usuário:
        "{question}"

        ### Dados Retornados do Banco de Dados:
        {db_result}

        ### Resposta:
    """
    try:
        response = client.chat.completions.create(
            model="llama3.2-vision:11b-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente prestativo que explica resultados de banco de dados."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.7,
            max_tokens  = 500
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Ocorreu um erro ao gerar a resposta final: {e}"