# pylint: disable=E1101
import grpc

from src.services.health.proto import health_pb2, health_pb2_grpc


class HealthServicer(health_pb2_grpc.HealthServicer):
    """Class for Health check service."""

    def __init__(self) -> None:
        self._server_status = {"": health_pb2.HealthCheckResponse.SERVING}

    def Check( #noqa: N802
        self,
        request: health_pb2.HealthCheckRequest,
        context: grpc.ServicerContext,
    ) -> health_pb2.HealthCheckResponse:  # ignore: C0103
        """Health check method.

        Args:
            request (health_pb2.HealthCheckRequest): Request body
            context (grpc.ServicerContext): context

        Returns:
            health_pb2.HealthCheckResponse: health check response
        """
        status = self._server_status.get(request.service)
        if status is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return health_pb2.HealthCheckResponse()
        return health_pb2.HealthCheckResponse(status=status)
