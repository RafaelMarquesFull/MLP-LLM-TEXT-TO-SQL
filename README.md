# 🚀 Sistema Híbrido Text-to-SQL com MLP e LLM
Este projeto implementa um sistema avançado capaz de traduzir perguntas em linguagem natural (português) para consultas SQL executáveis. A arquitetura é híbrida, utilizando um modelo de Machine Learning (MLP) para uma rápida classificação de intenção e um Large Language Model (LLM - qualquer modelo compativel com SDK da OpenAI) para a geração de consultas SQL complexas e respostas em linguagem natural.

O projeto é gerenciado por uma interface de linha de comando (CLI) construída sobre o FastMCP, que orquestra o ciclo de vida da aplicação e a execução de ferramentas modulares.

## 🏛️ Arquitetura
O fluxo de trabalho principal para responder a uma pergunta é o seguinte:

Entrada do Usuário: O usuário insere uma pergunta em português (ex: "quantos carros suv e automáticos existem?").

Classificação de Intenção (MLP): Um modelo de Regressão Logística, treinado localmente, classifica a intenção principal da pergunta (ex: GROUP_COUNT).

Geração de SQL (LLM): O LLM recebe a pergunta original, a intenção classificada pelo MLP e o schema detalhado do banco de dados. Com todo esse contexto, ele gera uma consulta SQL precisa e complexa.

Execução da Consulta: A consulta SQL é executada no banco de dados SQLite local.

Resposta em Linguagem Natural (LLM): O resultado da consulta é enviado de volta ao LLM, que gera uma resposta final amigável e contextualizada para o usuário.

## 🚀 Como Começar
### Siga os passos abaixo para configurar e executar o projeto.

#### 1. Pré-requisitos
    - Docker

    - Visual Studio Code

    - Extensão Dev Containers da Microsoft para o VS Code.

#### 2. Instalação com Dev Container
Este projeto está configurado para usar Dev Containers, o que simplifica drasticamente a configuração.

 - Clone o repositório:

        git clone https://github.com/RafaelMarquesFull/MLP-LLM-TEXT-TO-SQL
        
        cd MLP-LLM-TEXT-TO-SQL

- Abra no VS Code:
Abra a pasta do projeto no Visual Studio Code.

- Inicie o Dev Container:
O VS Code detectará automaticamente o arquivo .devcontainer/devcontainer.json e sugerirá reabrir o projeto em um contêiner. Clique em "Reopen in Container".

- O Dev Container irá construir o ambiente, instalar todas as dependências do Python com o Poetry e configurar tudo o que você precisa. Nenhuma instalação manual é necessária.

#### 3. Configuração da API da OpenAI
Para que o sistema possa gerar consultas SQL e respostas, ele precisa de acesso à API da OpenAI.

Altere o arquivo chamado ``.env_exemple`` na raiz do projeto para ``.env``.

Adicione sua chave de API da do seu modelo compativel com OPENAI da seguinte forma ou alter se ja existir no arquivo:

    OPENAI_API_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

Adicione o modelo LLM que deseja usar:

    OPENAI_API_MODEL="O MODELO DE SUA PREFERENCIA"

    
- OBS: 
    O modelo LLM utilizado nesse projeto voce pode encontrar em:
    [RaillsAI - LLMs for Production](https://www.raillsai.com)

    > ⚠️ **IMPORTANTE**: FOI DEIXADO UM MODELO DEFAULT EM `env_exemple` PARA TESTES

### 🛠️ Utilizando as Ferramentas
O projeto é executado através de uma única interface de linha de comando. Para iniciá-la, abra um terminal dentro do VS Code (que já estará no ambiente do Dev Container) e execute:

    poetry run python run_mcp.py

- Você verá um menu com as ferramentas disponíveis. O fluxo de trabalho recomendado é:

#### Ferramenta 1: popular_banco
Esta ferramenta cria o banco de dados automobiles.db e o preenche com os dados iniciais. Deve ser executada primeiro.

Como usar:
No menu principal, digite popular_banco e pressione Enter.

> popular_banco

#### Ferramenta 2: treinar_modelo
Esta ferramenta treina o modelo de classificação de intenção (MLP) e o salva na pasta /models. Ela também recarrega o modelo treinado para a sessão atual, permitindo o uso imediato da ferramenta perguntar.

Como usar:
No menu principal, digite treinar_modelo e pressione Enter.

> treinar_modelo

#### Ferramenta 3: perguntar
A principal ferramenta do sistema. Após treinar o modelo, você pode usá-la para fazer perguntas em linguagem natural ao seu banco de dados.

## Como usar:

No menu principal, digite perguntar.

O sistema solicitará que você insira a sua pergunta.

Digite a ``perguntar`` e pressione Enter:
    
    perguntar

Exemplos de Perguntas:

> perguntar
   -> Digite o valor para 'perguntar': quantos carros da audi existem?

> perguntar
   -> Digite o valor para 'perguntar': qual o preço médio dos carros automáticos do tipo suv?

> perguntar
   -> Digite o valor para 'perguntar': mostre os 5 carros mais caros.

Para sair da aplicação, digite sair.

### ✅ Executando os Testes
O projeto possui uma suíte de testes automatizados para garantir a qualidade e o funcionamento das principais ferramentas.

Para executar os testes, utilize o pytest através do Poetry no terminal do Dev Container:

    poetry run pytest

A saída deve indicar que todos os testes foram executados com sucesso (... passed).