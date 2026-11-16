README: PetBot - Atendimento inicial do pet shop

Nome do chatbot: PetBot
Tema: Atendimento inicial de um pet shop (serviços, preços, duração, agendamento, porte aceito, cuidados e informações da loja)
Integrantes: [preencher]

Objetivo do chatbot:
Responder às perguntas frequentes dos clientes com regras e palavras-chave. Quando as regras não reconhecem a pergunta, o bot consulta um modelo de linguagem (LLM) pela API gratuita da NVIDIA.

Descrição da base de dados:
Arquivo dados.csv com 21 serviços fictícios e 8 atributos: servico, categoria, descricao, porte_aceito, preco_a_partir, duracao_min, agendamento_necessario e observacao (orientações práticas, como o que levar, jejum ou atendimento por ordem de chegada). As informações da loja (horário, pagamento, endereço e contato) ficam no dicionário informacoes_loja do código. Todos os dados são pedagógicos e não substituem as informações reais do pet shop.

Intenções implementadas:
- agendamento: "agendar", "marcar"
- preco: "quanto custa", "preço", "valor"
- duracao: "quanto tempo", "demora"
- descricao: "o que inclui", "como funciona"
- porte: "porte", "tamanho"
- listar: "liste", "quais serviços", "mostre"

Assuntos da loja:
- horario: "horário", "abre", "fecha", "domingo"
- pagamento: "pagamento", "pix", "cartão", "parcela"
- endereco: "endereço", "onde fica", "estacionamento"
- contato: "telefone", "whatsapp", "contato"

Principais funcionalidades:
- Identificação do serviço pelo nome, com prioridade para o nome mais longo.
- Consultas com Pandas (filtros por nome e por categoria).
- Respostas completas: além da informação pedida, o bot informa o preço em reais, a duração, as orientações do serviço e como agendar.
- Respostas sobre horário, formas de pagamento, endereço e contato da loja.
- Detecção de emergências, com primeiros cuidados e orientação para procurar um veterinário.
- Camada LLM (API NVIDIA) para perguntas fora do escopo das regras.
- Interface Streamlit com histórico, filtro por categoria, visualização do DataFrame e chave para ligar ou desligar o LLM.

Melhoria desenvolvida pelo grupo:
Camada híbrida: as regras respondem às perguntas frequentes e um LLM responde às perguntas que as regras não reconhecem. O prompt envia o catálogo do dados.csv e as informações da loja ao modelo, para que as respostas usem os dados da base e terminem com o próximo passo para o cliente.
Funcionamento: se o serviço não for reconhecido ou a intenção for desconhecida, perguntar_llm() envia a pergunta à API e exibe a resposta.
Modelo usado: nvidia/nemotron-3.5-bolt-e4b. Se a API falhar, a mensagem do bot mostra o código do erro.

Limitações identificadas:
- Não consulta agenda real nem confirma disponibilidade.
- Os preços e horários são fictícios.
- O reconhecimento por palavras-chave depende das palavras escritas exatamente como estão no dicionário.
- O LLM depende de internet e de uma chave válida. Sem elas, o bot informa que o assistente não está disponível.
- A resposta do LLM não é verificada pelas regras. Por isso, deve ser usada apenas para orientação inicial.

Exemplos de perguntas que o chatbot consegue responder:
- Quanto custa um banho?
- Quanto tempo leva o banho e tosa?
- Como agendar a vacinação?
- O que inclui o exame de sangue?
- Qual o porte aceito pela hidratação de pelos?
- Liste os serviços de Saúde
- Qual o horário de funcionamento?
- Vocês aceitam Pix?
- Onde fica a loja?

Exemplos de perguntas fora das regras (resposta pelo LLM):
- Meu cachorro é idoso, qual serviço vocês recomendam?
- Meu gato tem medo de banho, o que vocês recomendam?

