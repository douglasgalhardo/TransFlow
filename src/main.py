import os
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List
from src.models.corrida_model import Corrida
from src.database.mongo_client import get_collection
from src.database.redis_client import get_redis
from src.producer import publish_corrida_event

app = FastAPI(title="TransFlow - API de Corridas Urbanas")

mongo_collection = get_collection()
redis_client = get_redis()

@app.post("/corridas", status_code=202, summary="Cadastrar nova corrida")
async def criar_corrida(corrida: Corrida, background_tasks: BackgroundTasks):
    """
    Recebe os dados da corrida e publica um evento assíncrono no RabbitMQ.
    O processamento (saldo e persistência) ocorre em segundo plano pelo worker.
    """
    # Publica no broker via BackgroundTasks para não bloquear a resposta HTTP
    background_tasks.add_task(publish_corrida_event, corrida.dict())
    
    return {
        "status": "processando", 
        "mensagem": "Corrida enviada para fila de processamento.",
        "id_corrida": corrida.id_corrida
    }

@app.get("/corridas", response_model=List[Corrida], summary="Listar todas as corridas")
async def listar_corridas():
    """Busca todas as corridas já processadas e salvas no MongoDB."""
    cursor = mongo_collection.find({})
    docs = await cursor.to_list(length=1000)
    return docs

@app.get("/corridas/{forma_pagamento}", response_model=List[Corrida], summary="Filtrar por pagamento")
async def filtrar_por_pagamento(forma_pagamento: str):
    """Filtra corridas no MongoDB pelo campo forma_pagamento."""
    cursor = mongo_collection.find({"forma_pagamento": forma_pagamento})
    docs = await cursor.to_list(length=1000)
    return docs

@app.get("/saldo/{motorista}", summary="Consultar saldo do motorista")
async def obter_saldo(motorista: str):
    """
    Consulta o saldo acumulado em tempo real no Redis.
    """
    key = f"saldo:{motorista.lower()}"
    value = await redis_client.get(key)
    
    saldo_float = 0.0
    if value:
        try:
            saldo_float = float(value)
        except ValueError:
            pass

    return {
        "motorista": motorista,
        "saldo_acumulado": saldo_float
    }