🚖 TransFlow - Backend de Corridas Urbanas

Protótipo de sistema distribuído para gestão de corridas, utilizando arquitetura orientada a eventos.

🏗️ Arquitetura

O sistema é composto por:

API (FastAPI): Recebe requisições e publica eventos.

Worker (FastStream): Consome eventos do RabbitMQ, atualiza Redis e MongoDB.

RabbitMQ: Broker de mensagens.

Redis: Cache para controle atômico de saldo.

MongoDB: Banco de dados persistente das corridas.

🚀 Como Executar

Pré-requisitos

Docker e Docker Compose instalados.

Passos

Certifique-se de que as portas 8000, 27017, 6379 e 5672 estão livres.

Execute o comando na raiz do projeto:

docker-compose up --build

Aguarde os logs indicarem que os serviços subiram.

🧪 Testando a API

O Swagger UI estará disponível em: http://localhost:8000/docs

1. Cadastrar Corrida (POST)

Envie uma requisição para /corridas:

{
"id_corrida": "run_001",
"passageiro": { "nome": "João", "telefone": "99999-1111" },
"motorista": { "nome": "Carla", "nota": 4.8 },
"origem": "Centro",
"destino": "Inoã",
"valor_corrida": 35.50,
"forma_pagamento": "DigitalCoin"
}

2. Verificar Saldo (GET)

Imediatamente após, verifique se o worker processou e atualizou o saldo:

Rota: /saldo/Carla

Resultado esperado: 35.5

3. Consultar Histórico (GET)

Verifique a persistência no MongoDB:

Rota: /corridas

🔧 Estrutura de Pastas

transflow/
├── src/
│ ├── database/ (mongo_client.py, redis_client.py)
│ ├── models/ (corrida_model.py)
│ ├── consumer.py
│ ├── main.py
│ └── producer.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

## Imagens

- [Swagger](https://drive.google.com/file/d/17tMxraGl6miHd-3Hc1Sry8l9QvkrwflH/view?usp=sharing)
- [GET /corridas](https://drive.google.com/file/d/1wXZFXEjGut9zY1XppFmtOOfMIQPUYzxl/view?usp=sharing)
- [GET /Saldo](https://drive.google.com/file/d/1IBhtUlNZfLkuVbhT5y1VHI1Ai8Ba32vY/view?usp=sharing)
- [Post /Corridas](https://drive.google.com/file/d/1nN_40X4wT26OovRsqs_ewD4T4LoSX8WG/view?usp=sharing)
