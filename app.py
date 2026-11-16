import os
import requests
import pandas as pd
import streamlit as st

URL_LLM = "https://integrate.api.nvidia.com/v1/chat/completions"
MODELO_LLM = "nvidia/nemotron-3.5-bolt-e4b"  # confirme o modelo disponível em build.nvidia.com

st.set_page_config(page_title="PetBot | Romeu Studio", layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("dados.csv")

palavras_emergencia = ["sangrando", "sangramento", "sangrou", "convulsão", "convulsao", "envenenado", "envenenou",
                       "desmaiou", "não respira", "nao respira", "atropelado", "engasgou", "engasgado"]

intencoes = {
    "agendamento": ["agendar", "marcar", "agendamento"],
    "preco": ["quanto custa", "preço", "preco", "valor"],
    "duracao": ["quanto tempo", "demora", "duração", "duracao"],
    "descricao": ["o que inclui", "como funciona", "o que é"],
    "porte": ["porte", "tamanho"],
    "listar": ["liste", "listar", "quais serviços", "quais servicos", "mostre"]
}

# informações da loja (fictícias), as perguntas mais comuns do dia a dia
NOME_LOJA = "Romeu Studio"
WHATSAPP = "(11) 90000-0000"

informacoes_loja = {
    "nome": "Somos o " + NOME_LOJA + ", pet shop com serviços de higiene, saúde, hospedagem, adestramento, transporte e alimentação para cães e gatos.",
    "horario": "Funcionamos de segunda a sexta, das 8h às 19h, e aos sábados, das 8h às 14h. Fechamos aos domingos e feriados.",
    "pagamento": "Aceitamos Pix, dinheiro e cartões de débito e crédito. Serviços acima de R$ 200,00 podem ser parcelados em até 3 vezes sem juros no crédito.",
    "endereco": "O " + NOME_LOJA + " fica na Rua das Flores, 123, Centro, com estacionamento gratuito para clientes. Se preferir, o serviço Transporte pet busca e entrega o seu pet em casa.",
    "contato": "Fale com a equipe pelo WhatsApp " + WHATSAPP + " ou pelo telefone (11) 3000-0000, no horário de funcionamento."
}

palavras_loja = {
    "nome": ["nome da loja", "nome do pet shop", "como se chama a loja"],
    "horario": ["horário", "horario", "que horas", "abre", "fecha", "funcionamento", "domingo", "sábado", "sabado", "feriado"],
    "pagamento": ["pagamento", "pagar", "pix", "cartão", "cartao", "dinheiro", "parcela", "crédito", "credito", "débito", "debito"],
    "endereco": ["endereço", "endereco", "onde fica", "localização", "localizacao", "estacionamento"],
    "contato": ["telefone", "whatsapp", "contato", "falar com"]
}

def descobrir_intencao(pergunta):
    texto = pergunta.lower()
    for intencao, palavras in intencoes.items():
        for palavra in palavras:
            if palavra in texto:
                return intencao
    return "desconhecida"

def descobrir_assunto_loja(pergunta):
    texto = pergunta.lower()
    for assunto, palavras in palavras_loja.items():
        for palavra in palavras:
            if palavra in texto:
                return assunto
    return None

def descobrir_servico(pergunta, dataframe):
    texto = pergunta.lower()
    encontrados = [servico for servico in dataframe["servico"] if servico.lower() in texto]
    if not encontrados:
        return None
    return max(encontrados, key=len)  # o nome mais longo vence: "Banho e tosa" vence "Banho"

def buscar_servico(servico, dataframe):
    resultado = dataframe[dataframe["servico"].str.lower() == servico.lower()]
    if len(resultado) == 0:
        return None
    return resultado.iloc[0]

def formatar_preco(valor):
    return f"R$ {float(valor):.2f}".replace(".", ",")  # 60 vira "R$ 60,00"

def formatar_duracao(minutos):
    if minutos < 60:
        return f"{minutos} minutos"
    horas = minutos // 60
    if horas == 1:
        return "1 hora"
    return f"{horas} horas"

def como_agendar(item):
    if item["agendamento_necessario"] == "Sim":
        return (f"{item['servico']} precisa de agendamento: chame no WhatsApp {WHATSAPP} "
                "informando o nome, a raça e o porte do pet, ou agende direto na loja.")
    return f"{item['servico']} não precisa de agendamento: é só vir à loja no horário de funcionamento."

def resumo_servico(item):
    minutos = int(item["duracao_min"])
    texto = f"{item['servico']}: {item['descricao']}. Preço a partir de {formatar_preco(item['preco_a_partir'])}"
    if minutos > 0:
        texto = texto + f", com duração de cerca de {formatar_duracao(minutos)}"
    return texto + f". {item['observacao']} {como_agendar(item)}"

def perguntar_llm(pergunta, dataframe):
    chave = os.getenv("NVIDIA_API_KEY")
    if not chave:
        return "O assistente avançado não está configurado. Fale com a equipe pelo WhatsApp " + WHATSAPP + "."
    catalogo = dataframe.to_string(index=False)
    loja = "\n".join(informacoes_loja.values())
    instrucao = ("Você é o PetBot, atendente virtual do pet shop " + NOME_LOJA + ". "
                 "Quando falar da loja, chame-a pelo nome " + NOME_LOJA + ". Responda em português, de forma clara e prática, "
                 "em até 4 frases, somente sobre o pet shop e os cuidados com pets. "
                 "Use apenas as informações abaixo e não invente preços, serviços ou horários. "
                 "Quando indicar um serviço, informe o preço inicial e se precisa de agendamento. "
                 "Termine com o próximo passo para o cliente, como agendar pelo WhatsApp ou vir à loja. "
                 "Se a informação não estiver abaixo, diga que não sabe e indique o contato da loja. "
                 "Em caso de emergência ou sintoma grave, oriente a procurar um veterinário imediatamente.\n\n"
                 "Informações da loja:\n" + loja + "\n\nCatálogo de serviços:\n" + catalogo)
    dados = {
        "model": MODELO_LLM,
        "messages": [{"role": "system", "content": instrucao},
                     {"role": "user", "content": pergunta}],
        "max_tokens": 2048,
        "temperature": 0.2
    }
    try:
        resposta = requests.post(URL_LLM, headers={"Authorization": "Bearer " + chave},
                                 json=dados, timeout=60)
        if resposta.status_code != 200:
            return f"No momento não consigo responder (erro {resposta.status_code}). Fale com a equipe pelo WhatsApp {WHATSAPP}."
        mensagem = resposta.json()["choices"][0]["message"]
        # alguns modelos colocam o texto em "reasoning_content" e deixam "content" vazio
        texto = mensagem.get("content") or mensagem.get("reasoning_content") or ""
        if texto == "":
            return "No momento não consigo responder essa pergunta. Fale com a equipe pelo WhatsApp " + WHATSAPP + "."
        return texto
    except (requests.RequestException, KeyError, IndexError):
        return "No momento não consigo responder essa pergunta. Fale com a equipe pelo WhatsApp " + WHATSAPP + "."

def chatbot(pergunta, dataframe, usar_llm=True):
    texto = pergunta.lower().strip()
    if not texto:
        return "Digite uma pergunta para que eu possa ajudar."

    if any(palavra in texto for palavra in palavras_emergencia):
        return ("Atenção: isso pode ser uma emergência. Leve o pet a um pronto-socorro veterinário 24 horas imediatamente. "
                "Enquanto isso, mantenha o pet calmo e aquecido, não dê remédios por conta própria e, se houver "
                "sangramento, pressione o local com um pano limpo. Se precisar, ligue para nós: " + WHATSAPP + ".")

    saudacoes = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]
    if any(s == texto or texto.startswith(s + " ") for s in saudacoes):
        return ("Olá! Bem-vindo ao " + NOME_LOJA + ". Eu sou o PetBot, o atendente virtual. Posso informar preço, duração, "
                "agendamento e cuidados de cada serviço, além do horário de funcionamento, das formas de "
                "pagamento, do endereço e do contato. Como posso ajudar?")

    frase = texto.replace("?", "").strip()  # a frase precisa ser exatamente uma destas
    if frase in ["ajuda", "preciso de ajuda", "o que você faz", "o que voce faz"]:
        return ("Você pode perguntar, por exemplo: 'Quanto custa um banho?', 'Como agendar a vacinação?', "
                "'O que inclui o exame de sangue?', 'Liste os serviços de Saúde', "
                "'Qual o horário de funcionamento?' ou 'Vocês aceitam Pix?'.")

    intencao = descobrir_intencao(pergunta)

    if intencao == "listar":
        for categoria in dataframe["categoria"].dropna().unique():
            if categoria.lower() in texto:
                encontrados = dataframe[dataframe["categoria"].str.lower() == categoria.lower()]
                itens = []
                for _, linha in encontrados.iterrows():
                    itens.append(f"{linha['servico']} (a partir de {formatar_preco(linha['preco_a_partir'])})")
                return f"Serviços de {categoria}: " + ", ".join(itens) + ". Pergunte sobre qualquer um deles para saber mais."
        partes = []
        for categoria in dataframe["categoria"].unique():
            nomes = dataframe[dataframe["categoria"] == categoria]["servico"].tolist()
            partes.append(f"{categoria}: " + ", ".join(nomes))
        return "Nossos serviços por categoria. " + ". ".join(partes) + ". Para ver os preços, peça, por exemplo, 'Liste os serviços de Higiene'."

    servico = descobrir_servico(pergunta, dataframe)
    if servico is None or intencao == "desconhecida":
        assunto = descobrir_assunto_loja(pergunta)
        if assunto is not None:
            return informacoes_loja[assunto]
        if usar_llm:
            return perguntar_llm(pergunta, dataframe)
        if servico is not None:
            return resumo_servico(buscar_servico(servico, dataframe))
        return ("Ainda não entendi. Pergunte sobre preço, duração, agendamento, descrição ou porte de um serviço, "
                "ou sobre horário, pagamento, endereço e contato. Se preferir, fale com a equipe pelo WhatsApp " + WHATSAPP + ".")

    item = buscar_servico(servico, dataframe)
    minutos = int(item["duracao_min"])
    if intencao == "preco":
        return (f"{servico} custa a partir de {formatar_preco(item['preco_a_partir'])}. O valor final é confirmado "
                f"no atendimento, conforme o porte e as condições do pet. {como_agendar(item)}")
    elif intencao == "duracao":
        if minutos == 0:
            return f"{servico} é um produto: pode ser comprado direto na loja, sem espera. {item['observacao']}"
        return f"{servico} leva cerca de {formatar_duracao(minutos)}. {item['observacao']} {como_agendar(item)}"
    elif intencao == "agendamento":
        return f"{como_agendar(item)} {item['observacao']}"
    elif intencao == "descricao":
        return resumo_servico(item)
    elif intencao == "porte":
        if item["porte_aceito"] == "Todos":
            return f"{servico} atende pets de todos os portes. {item['observacao']}"
        return f"{servico} atende pets de porte {item['porte_aceito'].lower()}. {item['observacao']}"
    return resumo_servico(item)

df = carregar_dados()

st.title("PetBot | " + NOME_LOJA)
st.caption("Atendimento inicial do pet shop " + NOME_LOJA + " | Python + Pandas + Streamlit + LLM (NVIDIA)")

with st.sidebar:
    st.header("Serviços")
    categoria_filtro = st.selectbox("Filtrar categoria", ["Todas"] + sorted(df["categoria"].unique().tolist()))
    if categoria_filtro == "Todas":
        lista = df
    else:
        lista = df[df["categoria"] == categoria_filtro]
    for servico in lista["servico"]:
        st.write("-", servico)

    st.divider()
    usar_llm = st.toggle("Usar assistente avançado (LLM)", value=True)

    st.divider()
    st.subheader("Experimente")
    st.write("Quanto custa um banho?")
    st.write("Como agendar a vacinação?")
    st.write("O que inclui o exame de sangue?")
    st.write("Liste os serviços de Saúde")
    st.write("Qual o horário de funcionamento?")
    st.write("Vocês aceitam Pix?")

    st.divider()
    if st.button("Limpar conversa"):
        st.session_state.mensagens = []
        st.rerun()

with st.expander("Investigar a base com Pandas"):
    st.dataframe(df, hide_index=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Serviços", len(df))
    col2.metric("Categorias", df["categoria"].nunique())
    col3.metric("Com agendamento", len(df[df["agendamento_necessario"] == "Sim"]))

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# o Streamlit entende texto entre dois "$" como fórmula; "\$" mostra o cifrão normal
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["papel"]):
        st.write(mensagem["conteudo"].replace("$", "\\$"))

pergunta = st.chat_input("Pergunte sobre um serviço...")
if pergunta:
    st.session_state.mensagens.append({"papel": "user", "conteudo": pergunta})
    with st.chat_message("user"):
        st.write(pergunta.replace("$", "\\$"))

    resposta = chatbot(pergunta, df, usar_llm)
    st.session_state.mensagens.append({"papel": "assistant", "conteudo": resposta})
    with st.chat_message("assistant"):
        st.write(resposta.replace("$", "\\$"))
