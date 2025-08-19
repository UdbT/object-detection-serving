import logging

import cv2
import numpy as np

import onnxruntime as ort

from src.config import settings
from src.utils import sigmoid, xywh_to_xyxy

logger = logging.getLogger(__name__)


class ObjectDetection:
    """Class for Object Detection Model."""

    def __init__(self, model_path: str) -> None:
        """Initialize the Object Detection model.
        Args:
            model_path (str): Path to the ONNX model file.
        """
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape
        self.height, self.width = self.input_shape[2], self.input_shape[3]

        logger.info("Object Detection ONNX model has been initialized")

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the input image for the model.

        Args:
            image (np.ndarray): input image

        Returns:
            np.ndarray: preprocessed image
        """
        resized_image = cv2.resize(image, (self.width, self.height))  # Resize to model input size
        img_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img_norm = img_rgb.astype(np.float32) / 255.0  # Normalize to [0, 1]
        img_transposed = np.transpose(img_norm, (2, 0, 1))  # HWC → CHW
        img_input = np.expand_dims(img_transposed, axis=0)
        return img_input

    def infer(self, preprocessed_image: np.ndarray) -> np.ndarray:
        """Run inference on the input image.

        Args:
            image (np.ndarray): input image

        Returns:
            np.ndarray: model outputs
        """
        outputs = self.session.run([self.output_name], {self.input_name: preprocessed_image})[0]
        return outputs

    def postprocess(self, preds: np.ndarray, image_shape: tuple[int, int]) -> dict:
        """Postprocess the model outputs to extract bounding boxes and class labels.

        Args:
            outputs (np.ndarray): model outputs
            image_shape (tuple[int, int]): shape of the input image

        Returns:
            dict: a dictionary that includes predicted bounding boxes and class labels
        """
        preds = np.squeeze(preds, 0).transpose(1, 0)  #

        # Split fields
        boxes = preds[:, :4]
        cls_logits = preds[:, 4:]

        # Convert class logits -> probs (apply sigmoid unless already 0..1)
        if cls_logits.min() >= 0.0 and cls_logits.max() <= 1.0:
            cls_probs = cls_logits
        else:
            cls_probs = sigmoid(cls_logits)

        scores = cls_probs.max(axis=1)  # (N,)
        labels = cls_probs.argmax(axis=1)  # (N,)

        # Convert boxes to corners in input (640x640) space
        xyxy = xywh_to_xyxy(boxes)

        # Scale back to original image size
        sx = image_shape[1] / float(self.input_shape[3])
        sy = image_shape[0] / float(self.input_shape[2])
        xyxy[:, [0, 2]] *= sx
        xyxy[:, [1, 3]] *= sy

        # Confidence filter
        m = scores >= settings.conf_thres
        xyxy, scores, labels = xyxy[m], scores[m], labels[m]

        indices = cv2.dnn.NMSBoxes(
            bboxes=xyxy.tolist(),
            scores=scores.tolist(),
            score_threshold=settings.conf_thres,
            nms_threshold=settings.iou_thres,
        )

        detections = []
        if len(indices) > 0:
            for i in np.array(indices).reshape(-1):
                detections.append((xyxy[i], scores[i], settings.coco_classes[int(labels[i])]))
        logger.info(f"Detected {len(detections)} objects", extra={"detections": detections})
        return detections

    def forward(self, input_image: np.ndarray) -> dict:
        """Run the object detection model.

        Args:
            input_image (np.ndarray): input image

        Returns:
            dict: a dictionary that includes predicted bounding boxes and class labels
        """
        preprocessed_image = self.preprocess(input_image)
        outputs = self.infer(preprocessed_image)
        detections = self.postprocess(outputs, input_image.shape[:2])
        return {"detections": detections}

# ruff: noqa
if __name__ == "__main__":
    object_detector = ObjectDetection("src/services/object_detection/yolo11m-sim-shape.onnx")
    test_image = cv2.imread("src/services/object_detection/image.jpg")

    results = object_detector.forward(test_image)
    for bbox, score, label in results["detections"]:
        print(f"Detected {label} with confidence {score:.2f} at {bbox}")
# ruff: enable
