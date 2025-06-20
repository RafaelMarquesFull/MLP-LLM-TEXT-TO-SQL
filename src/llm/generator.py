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
            cols_to_sample      = ['body-style', 'transmission', 'fuel-type', 'drive-wheels', 'color']
            
            for col_name in cols_to_sample:
                if col_name in column_names:
                    cursor.execute(f'SELECT DISTINCT "{col_name}" FROM automobiles LIMIT 10')
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
        Você é um gerador de código SQL para SQLite. Sua única função é traduzir a pergunta de um usuário em uma única e válida consulta SQL, usando o conhecimento e as regras fornecidas.

        ### Conhecimento do Banco de Dados
        {db_context}

        ---
        ### Exemplo de Tarefa Perfeita
        - **Pergunta do Usuário:** "quais carros são da audi?"
        - **Intenção Principal (do MLP):** "LIST_ALL"
        - **SQL Gerado:** SELECT * FROM automobiles WHERE LOWER(make) = 'audi';
        ---

        ### Sua Tarefa Atual
        - **Pergunta do Usuário:** "{question}"
        - **Intenção Principal (do MLP):** "{intent}"

        ### Regras Obrigatórias
        1.  **Regra de Ouro: O resultado DEVE ser uma string de texto SQL, e NADA MAIS.** Não use JSON, Markdown, ou qualquer outro formato.
        2.  **Use a Intenção do MLP:** A "Intenção Principal" DEVE definir a operação principal da sua consulta. Se for 'COUNT', use `COUNT(*)`. Se for 'AVG_PRICE', use `AVG(price)`. Se for 'LIST_ALL', use `SELECT *`.
        3.  **Foco na Pergunta:** A cláusula `WHERE` deve ser construída para filtrar com base nos detalhes da "Pergunta do Usuário" atual.
        4.  **Sintaxe Correta:** A consulta deve ser sintaticamente perfeita para SQLite.
        5.  **Ignorar Maiúsculas/Minúsculas:** Sempre use `LOWER()` em colunas de texto para comparações na cláusula `WHERE`.
        
        ### SQL Gerado:
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_API_MODEL", "gpt-4o"), 
            messages=[
                {"role": "system", "content": "Você é um especialista em gerar consultas SQLite. Responda APENAS com a string SQL crua."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0,
            max_tokens  = 300
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
        if sql_query.startswith("`"):
            sql_query = sql_query[1:-1].strip()
            
        return sql_query
    
    except Exception as e:
        return f"SELECT 'ERRO ao chamar a API da OpenAI: {e}';"


def generate_natural_language_response(question: str, db_result: pd.DataFrame | str) -> str:
    
    prompt = f"""
        Sua tarefa é responder à pergunta original de um usuário de forma amigável e direta, com base nos dados que foram retornados de uma consulta ao banco de dados.

        ### Instruções de Formatação:
        - Gere a resposta em texto puro (plain text).
        - NÃO use formatação markdown, como `**` para negrito ou `*` para itens de lista.
        - Se os "Dados Retornados" contiverem uma mensagem de erro, explique o problema de forma simples ao usuário, sem repetir a mensagem de erro técnica.

        ### Pergunta Original do Usuário:
        "{question}"

        ### Dados Retornados do Banco de Dados:
        {db_result}

        ### Resposta:
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_API_MODEL", "gpt-4o"), 
            messages=[
                {"role": "system", "content": "Você é um assistente prestativo que explica resultados de banco de dados."},
                {"role": "user", "content": prompt}
            ],
            temperature = 0.7,
            max_tokens  = 200
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Ocorreu um erro ao gerar a resposta final: {e}"
