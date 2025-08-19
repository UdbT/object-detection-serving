import asyncio

import grpc
from src.services.health.proto import health_pb2, health_pb2_grpc


async def run() -> None:
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = health_pb2_grpc.HealthStub(channel)
        response = await stub.Check(health_pb2.HealthCheckRequest())
    print(f"Health check received: {response.status}")


if __name__ == "__main__":
    asyncio.run(run())
