import asyncio
import time
from io import BytesIO

import cv2
import grpc
import numpy as np
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import (
    ProtoReflectionDescriptorDatabase,
)

from google.protobuf.descriptor_pool import DescriptorPool
from google.protobuf.message_factory import GetMessageClass

COCO_CLASSES = [
    "person","bicycle","car","motorcycle","airplane","bus","train","truck","boat","traffic light",
    "fire hydrant","stop sign","parking meter","bench","bird","cat","dog","horse","sheep","cow",
    "elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee",
    "skis","snowboard","sports ball","kite","baseball bat","baseball glove","skateboard","surfboard",
    "tennis racket","bottle","wine glass","cup","fork","knife","spoon","bowl","banana","apple","sandwich",
    "orange","broccoli","carrot","hot dog","pizza","donut","cake","chair","couch","potted plant","bed",
    "dining table","toilet","tv","laptop","mouse","remote","keyboard","cell phone","microwave","oven",
    "toaster","sink","refrigerator","book","clock","vase","scissors","teddy bear","hair drier","toothbrush"
]

def generate_request(request, req_id, image):
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

    with grpc.insecure_channel("localhost:50051") as channel:
        reflection_db = ProtoReflectionDescriptorDatabase(channel)
        desc_pool = DescriptorPool(reflection_db)
        service_desc = desc_pool.FindServiceByName("grpc.object_detection.v1.ObjectDetection")
        method_desc = service_desc.FindMethodByName("Forward")

        ObjectDetectionRequest = GetMessageClass(method_desc.input_type)
        ObjectDetectionResponse = GetMessageClass(method_desc.output_type)
        print(f"Service full name: {service_desc.full_name}")
        print(f"Method: {method_desc.name}")
        print(f"Request Class: {ObjectDetectionRequest}")
        print(f"Response Class: {ObjectDetectionResponse}")

    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        request_message = ObjectDetectionRequest()
        response_message = ObjectDetectionResponse()

        stub_method = channel.unary_unary(
            f"/{service_desc.full_name}/{method_desc.name}",
            request_serializer=request_message.SerializeToString,
            response_deserializer=response_message.FromString,
        )

        request_message = generate_request(
            request_message, "test_reflection_req_id", image
        )
        start_time = time.time()
        response = await stub_method(request_message)
        print(f"Response time: {time.time() - start_time}")

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    output = f"{image_folder}/output_{image_name}"
    img_annotated = draw_detections(image, response.objects)
    cv2.imwrite(output, img_annotated)
    print(f"output has been saved to {output}")


if __name__ == "__main__":
    asyncio.run(run())
