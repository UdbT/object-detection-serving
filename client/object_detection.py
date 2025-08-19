import asyncio
import time
from io import BytesIO

import cv2
import grpc
import numpy as np

from src.services.object_detection.proto import object_detection_pb2, object_detection_pb2_grpc


def generate_request(req_id, image):
    request = object_detection_pb2.ObjectDetectionRequest()
    request.req_id = req_id
    buffer = BytesIO()
    np.save(buffer, image)
    request.data = buffer.getvalue()
    return request


def draw_detections(img_bgr, detections):
    out = img_bgr.copy()
    # Draw bounding box and label
    for det in detections:
        bbox = det.bbox
        score = det.score
        label = det.label

        x1, y1, x2, y2 = bbox
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        # box
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # label
        label = f"{label} {score:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

        y_top = max(0, y1 - th - 6)
        cv2.rectangle(out, (x1, y_top), (x1 + tw + 6, y_top + th + 6), (0, 255, 0), -1)
        cv2.putText(out, label, (x1 + 3, y_top + th + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    return out

async def run() -> None:
    image_folder = "client"
    image_name = "image.jpg"
    image_path = f"{image_folder}/{image_name}"
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = object_detection_pb2_grpc.ObjectDetectionStub(channel)
        request = generate_request("test_id", image)
        start_time = time.time()
        response = await stub.Forward(request)
        print(f"response time: {time.time() - start_time}")
        print(f"number of objects: {len(response.objects)}")

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    output = f"{image_folder}/output_{image_name}"
    img_annotated = draw_detections(image, response.objects)
    cv2.imwrite(output, img_annotated)
    print(f"output has been saved to {output}")

if __name__ == "__main__":
    asyncio.run(run())
