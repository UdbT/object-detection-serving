import logging
from io import BytesIO

import grpc
import numpy as np

from src.config import settings
from src.services.object_detection.model import ObjectDetection
from src.services.object_detection.proto import object_detection_pb2, object_detection_pb2_grpc

logger = logging.getLogger(__name__)


class ObjectDetectionServicer(object_detection_pb2_grpc.ObjectDetectionServicer):
    """Object Detection servicer class."""

    _object_detector = ObjectDetection(settings.model_path)

    async def Forward( # noqa: N802
        self,
        request: object_detection_pb2.ObjectDetectionRequest,
        _context: grpc.aio.ServicerContext,
    ) -> object_detection_pb2.ObjectDetectionResponse:
        """Run object detection pipeline.

        Args:
            request (object_detection_pb2.ObjectDetectionRequest): input
            _context (grpc.aio.ServicerContext): context (not used)

        Returns:
            object_detection_pb2.ObjectDetectionResponse: output of model
        """
        req_id = request.req_id
        buffer = BytesIO(request.data)
        buffer.seek(0)
        image = np.load(buffer)

        results = self._object_detector.forward(image)
        detections = results["detections"]

        detected_objects = []
        for bbox, score, label in detections:
            detection = object_detection_pb2.DetectedObject(bbox=bbox, score=score, label=label)
            detected_objects.append(detection)
        return object_detection_pb2.ObjectDetectionResponse(req_id=req_id, objects=detected_objects)
