import logging
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection
from pythonjsonlogger import jsonlogger

from src.config import settings
from src.services.health import health_servicer
from src.services.object_detection import object_detection_servicer

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(settings.log_format))
logging.basicConfig(level=settings.log_level, handlers=(handler,))

logger = logging.getLogger(__name__)

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


async def serve() -> None:
    """Serving gRPC server for Face Landmark and health check."""
    # Initial gRPC Async server
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            (
                "grpc.max_receive_message_length",
                settings.grpc_max_receive_message_length,
            ),
        ],
    )

    # Adding services
    health_servicer.health_pb2_grpc.add_HealthServicer_to_server(health_servicer.HealthServicer(), server)
    object_detection_servicer.object_detection_pb2_grpc.add_ObjectDetectionServicer_to_server(
        object_detection_servicer.ObjectDetectionServicer(), server
    )

    # Enable reflector for object detection
    service_names = (
        object_detection_servicer.object_detection_pb2.DESCRIPTOR.services_by_name["ObjectDetection"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    # Adding port and start server
    listen_addr = f"[::]:{settings.port}"
    server.add_insecure_port(listen_addr)
    logger.info("Starting server on %s", listen_addr)
    await server.start()

    async def server_graceful_shutdown() -> None:
        """Graceful shutdown of the server."""
        logger.info("Starting graceful shutdown...")
        # Shuts down the server with 5 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())
    await server.wait_for_termination()
