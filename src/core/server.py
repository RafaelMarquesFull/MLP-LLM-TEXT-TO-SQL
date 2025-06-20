import  os
import  sqlite3
import  joblib
import  pandas                    as pd
from    typing                    import Dict, Any, Optional
from    pathlib                   import Path
from    contextlib                import asynccontextmanager
from    dataclasses               import dataclass
from    collections.abc           import AsyncIterator
from    src.llm.generator         import generate_sql_query, generate_natural_language_response
from    src.mlp.train             import train_model     as tool_train_model
from    src.database.populate_db  import create_database as tool_populate_db


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR   = PROJECT_ROOT / "models"
DATA_DIR     = PROJECT_ROOT / "data"
DB_PATH      = DATA_DIR     / "automobiles.db"

class FastMCP:
    
    def __init__(self, name: str, lifespan: Optional[callable] = None, **kwargs):
        
        self.name                                    = name
        self._lifespan                               = lifespan
        self._tools: Dict[str, callable]             = {}
        self._lifespan_context: Optional[AppContext] = None
        
        
    def tool(self, name: str):
        
        def decorator(func):
            self._tools[name] = func
            return func
        
        return decorator
    
    def get_context(self): return self._lifespan_context
    
    async def run_lifespan_startup(self):
        
        if  self._lifespan:
            self._lifespan_manager = self._lifespan(self)
            self._lifespan_context = await self._lifespan_manager.__aenter__()

    async def run_lifespan_shutdown(self):
        if hasattr(self, '_lifespan_manager') and self._lifespan_manager:
            print("🌙 Encerrando lifespan...")
            await self._lifespan_manager.__aexit__(None, None, None)

@dataclass
class AppContext:
    mlp_pipeline: Optional[Any]  = None
    label_encoder: Optional[Any] = None
    db_path: Path                = DB_PATH
    openai_available: bool       = False

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    
    print("\n--- INICIALIZANDO RECURSOS DA APLICAÇÃO ---")
    
    context      = AppContext()
    mlp_path     = MODELS_DIR / "intent_classification_pipeline.joblib"
    encoder_path = MODELS_DIR / "intent_label_encoder.joblib"
    
    try:
        context.mlp_pipeline  = joblib.load(mlp_path)
        context.label_encoder = joblib.load(encoder_path)
        print("   ✅ Modelo MLP e codificador carregados.")
        
    except FileNotFoundError:
        print("   ⚠️ AVISO: Modelos MLP não encontrados. Execute 'treinar_modelo'.")
    
    if os.getenv("OPENAI_API_KEY"):
        
        context.openai_available = True
        print("   ✅ Chave de API compativel com OpenAI encontrada.")
        
    else:
        print("   ⚠️ AVISO: Chave 'OPENAI_API_KEY' não encontrada.")
    
    try:
        yield context
        
    finally:
        print("\n--- RECURSOS ENCERRADOS ---")


mcp = FastMCP(
    name     ="Gerenciador Híbrido Text-to-SQL", 
    lifespan =app_lifespan
)

@mcp.tool(name="popular_banco")

async def populate_database_tool():
    
    try:
        tool_populate_db()
        return f"✅ Banco de dados criado com sucesso em '{DB_PATH}'!"
    
    except Exception as e: return f"❌ Erro: {e}"

@mcp.tool(name="treinar_modelo")
async def train_model_tool():
   
    print("\nIniciando treinamento do modelo...")
    try:
        
        tool_train_model()
        
        ctx               = mcp.get_context()
        mlp_path          = MODELS_DIR / "intent_classification_pipeline.joblib"
        encoder_path      = MODELS_DIR / "intent_label_encoder.joblib"
        
        ctx.mlp_pipeline  = joblib.load(mlp_path)
        ctx.label_encoder = joblib.load(encoder_path)
        
        return "✅ Treinamento concluído e modelos carregados na sessão!"

    except Exception as e:
        return f"❌ Erro durante o treinamento: {e}"


@mcp.tool(name="perguntar")
async def ask_question_tool(pergunta: str):
    
    ctx             = mcp.get_context()
    
    if not ctx.mlp_pipeline: return "❌ ERRO: Modelo MLP não carregado. Execute 'treinar_modelo'."
    if not ctx.openai_available: return "❌ ERRO: Chave da OpenAI não configurada."
   
    print(f"\n[Passo 1/4] Classificando intenção com MLP para: '{pergunta}'")
    
    predicted_code  = ctx.mlp_pipeline.predict(pd.Series([pergunta]))
    intent          = ctx.label_encoder.inverse_transform(predicted_code)[0]
    
    print(f"    -> Intenção prevista: {intent}")

    print("[Passo 2/4] Gerando consulta SQL com LLM (guiado pelo MLP)...")
    
    sql_query       = generate_sql_query(pergunta, intent)
    
    print(f"    -> SQL Gerado: {sql_query}")
    
    if "ERRO" in sql_query: return f"❌ {sql_query}"

    print("[Passo 3/4] Executando consulta no banco de dados...")
    
    try:
        with sqlite3.connect(ctx.db_path) as conn:
            db_result = pd.read_sql_query(sql_query, conn)
            
        print(f"    -> Resultado: {db_result.shape[0]} linhas retornadas.")
        
    except Exception as e:
        db_result = f"Erro ao executar a consulta SQL: {e}"
        print(f"    -> {db_result}")
    
    print("[Passo 4/4] Gerando resposta final em linguagem natural...")
    
    final_response = generate_natural_language_response(pergunta, db_result)

    return {
        "pergunta_original"     : pergunta,
        "intenção_prevista_mlp" : intent,
        "sql_gerado_llm"        : sql_query,
        "resposta_final"        : final_response
    }