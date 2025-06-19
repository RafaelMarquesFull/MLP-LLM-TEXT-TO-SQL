
import pytest
import pytest_asyncio 
import os
from unittest.mock      import patch
from src.core.server    import mcp, AppContext

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture(scope="module")
async def client():
  
    await mcp.run_lifespan_startup()
    yield mcp
    await mcp.run_lifespan_shutdown()


async def test_populate_database_tool(client):

    ctx: AppContext = client.get_context()
    db_path         = ctx.db_path

    if os.path.exists(db_path):
        os.remove(db_path)

    result          = await client._tools["popular_banco"]()

    assert "Banco de dados criado com sucesso" in result
    assert os.path.exists(db_path), "O arquivo do banco de dados não foi criado."


async def test_train_model_tool(client):
   
    ctx: AppContext = client.get_context()
    result          = await client._tools["treinar_modelo"]()
    
    assert "Treinamento concluído e modelos carregados" in result
    assert ctx.mlp_pipeline is not None, "O pipeline MLP não foi carregado no contexto."
    assert ctx.label_encoder is not None, "O LabelEncoder não foi carregado no contexto."


@patch("src.core.server.generate_sql_query")
@patch("src.core.server.generate_natural_language_response")
async def test_ask_question_tool(mock_generate_nlp, mock_generate_sql, client):

    ctx: AppContext                = client.get_context()
    
    if not ctx.mlp_pipeline:
        await client._tools["treinar_modelo"]()

    mocked_sql                     = "SELECT COUNT(*) FROM automobiles WHERE 'body-style' = 'suv';"
    mocked_nlp_response            = "Existem 5 carros SUV."
    mock_generate_sql.return_value = mocked_sql
    mock_generate_nlp.return_value = mocked_nlp_response
    test_question                  = "quantos suvs existem?"
    result                         = await client._tools["perguntar"](pergunta=test_question)

    mock_generate_sql.assert_called_once()
    mock_generate_nlp.assert_called_once()
    
    assert result["pergunta_original"]  == test_question
    assert result["sql_gerado_llm"]     == mocked_sql
    assert result["resposta_final"]     == mocked_nlp_response
    assert result["intenção_prevista_mlp"] is not None, "A intenção do MLP não foi prevista."
