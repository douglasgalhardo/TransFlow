import os
import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from src.database.redis_client import get_redis
from src.database.mongo_client import get_collection
from src.models.corrida_model import Corrida

# Configurações do RabbitMQ
RABBIT_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBIT_PASS = os.getenv('RABBITMQ_PASSWORD', 'guest')
# ATENÇÃO: O host padrão agora é 'rabbitmq' (nome do serviço no docker-compose)
RABBIT_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq') 
RABBIT_PORT = os.getenv('RABBITMQ_PORT', 5672)
RABBIT_URL = f"amqp://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}/"
RABBIT_QUEUE = os.getenv("RABBITMQ_QUEUE", "corrida_finalizada")

# Inicialização do Broker e App FastStream
broker = RabbitBroker(RABBIT_URL)
app_stream = FastStream(broker)

# Clientes de Banco de Dados
redis_client = get_redis()
mongo_collection = get_collection()

@broker.subscriber(RABBIT_QUEUE)
async def handle_corrida_event(corrida: dict) -> None:
    """
    Consumer que processa o evento de 'corrida_finalizada'.
    """
    print(f"📥 [Consumer] Recebido evento de corrida: {corrida.get('id_corrida')}")
    
    try:
        data = Corrida(**corrida)
        motorista_nome = data.motorista.nome.lower()
        saldo_key = f"saldo:{motorista_nome}"
        valor = float(data.valor_corrida)

        # --- 1. Atualização Atômica no Redis ---
        async with redis_client.client() as conn:
            await conn.watch(saldo_key)
            try:
                multi = conn.multi_exec()
                multi.incrbyfloat(saldo_key, valor)
                await multi.execute()
                print(f"💰 [Redis] Saldo atualizado para {motorista_nome}: +{valor}")
            except Exception as e:
                print(f"⚠️ [Redis] Falha na transação, tentando fallback: {e}")
                await conn.incrbyfloat(saldo_key, valor)

        # --- 2. Persistência no MongoDB ---
        await mongo_collection.update_one(
            {"id_corrida": data.id_corrida},
            {"$set": data.dict()},
            upsert=True
        )
        print(f"💾 [Mongo] Corrida {data.id_corrida} salva com sucesso.")

    except Exception as e:
        print(f"❌ [Erro] Falha ao processar mensagem: {e}")

async def main():
    # Loop de conexão robusto (Retry Pattern)
    while True:
        try:
            print(f"⏳ [Worker] Tentando conectar ao RabbitMQ em {RABBIT_HOST}...")
            await app_stream.run()
            break # Se conectar e rodar, sai do loop quando encerrar
        except Exception as e:
            print(f"⚠️ [Worker] Falha na conexão ({e}). Tentando novamente em 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())