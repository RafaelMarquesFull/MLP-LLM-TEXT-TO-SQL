
import asyncio
import inspect
from src.core.server import mcp

async def main_cli():

    await mcp.run_lifespan_startup()

    print("\n" + "="*50)
    print("   🤖 Gerenciador de Projeto Híbrido MLP-LLM-Text-to-SQL 🤖")
    print("="*50)

    while True:
        try:
            print("\nFerramentas disponíveis:")
            
            for tool_name in mcp._tools:
                print(f"  - {tool_name}")
                
            print("\nDigite o nome da ferramenta ou 'sair' para encerrar.")
            
            command = input("> ").strip().lower()

            if command in ['sair', 'exit']:
                break

            if command not in mcp._tools:
                print(f"❌ Comando inválido: '{command}'")
                continue

            tool_func    = mcp._tools[command]
            params       = inspect.signature(tool_func).parameters
            args_to_pass = {}
            
            for param_name, param in params.items():
                
                if param.default == inspect.Parameter.empty:
                    
                    arg_value = input(f"   -> Digite o valor para '{param_name}': ")
                    
                    args_to_pass[param_name] = arg_value
            
            print("\n--- EXECUTANDO FERRAMENTA ---")
            
            result = await tool_func(**args_to_pass)
            
            print("--- RESULTADO ---")
            
            if isinstance(result, dict):
                
                for key, value in result.items():
                    if key != 'resposta_final':
                        print(f"  {key.replace('_', ' ').capitalize()}: {value}")
                    else:
                        print("--- RESPOSTA ---")
                        print(value)
            else:
                print(result)
                
            print("-----------------")

        except KeyboardInterrupt:
            
            print("\nSaindo...")
            break
        
        except Exception as e:
            print(f"\n💥 Ocorreu um erro inesperado: {e}")
            import traceback
            traceback.print_exc()

    await mcp.run_lifespan_shutdown()

if __name__ == "__main__":
    try:
        
        asyncio.run(main_cli())
        
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário.")
