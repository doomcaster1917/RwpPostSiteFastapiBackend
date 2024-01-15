from redis import asyncio as aioredis

async def redis_server():
    redis = await aioredis.Redis(host='localhost', port=6379, decode_responses=True)
    return redis
