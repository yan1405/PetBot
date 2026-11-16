# PetBot

Chatbot de atendimento inicial do **Romeu Studio**, um pet shop fictício, feito como trabalho do curso técnico de IA.

O PetBot responde às perguntas frequentes com regras, palavras-chave e consultas com Pandas sobre o arquivo `dados.csv`. Quando as regras não reconhecem a pergunta, ele consulta um modelo de linguagem (LLM) pela API da NVIDIA.

## Arquivos

- `app.py`: aplicação em Streamlit.
- `chatbot.ipynb`: notebook com a construção do chatbot passo a passo.
- `dados.csv`: base fictícia com 21 serviços do Romeu Studio.
- `README.txt`: documentação do trabalho.
- `requirements.txt`: bibliotecas usadas (pandas, requests e streamlit).

## Como executar

1. Instale as bibliotecas: `pip install -r requirements.txt`
2. Defina a chave da API da NVIDIA (sem colocá-la nos arquivos):
   - Windows (PowerShell): `$env:NVIDIA_API_KEY="nvapi-..."`
   - Linux/macOS: `export NVIDIA_API_KEY="nvapi-..."`
3. Execute na pasta do projeto: `python -m streamlit run app.py`

Sem a chave, as regras funcionam normalmente e apenas a parte do LLM fica indisponível.

## Publicação no Streamlit Community Cloud

A chave é cadastrada em **Settings > Secrets** do app, nunca no código:

```
NVIDIA_API_KEY = "nvapi-..."
```
