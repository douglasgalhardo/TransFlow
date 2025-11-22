import os
from faststream.rabbit import RabbitBroker

# Configurações
RABBIT_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBIT_PASS = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBIT_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBIT_PORT = os.getenv('RABBITMQ_PORT', 5672)
RABBIT_URL = f"amqp://{RABBIT_USER}:{RABBIT_PASS}@{RABBIT_HOST}:{RABBIT_PORT}/"
RABBIT_QUEUE = os.getenv("RABBITMQ_QUEUE", "corrida_finalizada")

async def publish_corrida_event(corrida_payload: dict):
    """
    Conecta ao RabbitMQ e publica o evento de corrida finalizada.
    """
    async with RabbitBroker(RABBIT_URL) as broker:
        await broker.publish(
            message=corrida_payload,
            queue=RABBIT_QUEUE
        )
        print(f"📤 [Producer] Evento publicado: {corrida_payload.get('id_corrida')}")