import numpy as np


def sigmoid(mat: np.ndarray) -> np.ndarray:
    """Apply sigmoid activation function to a numpy array.

    Args:
        mat (np.ndarray): Input array.

    Returns:
        np.ndarray: Sigmoid activated array.
    """
    return 1.0 / (1.0 + np.exp(-mat))


def xywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
    """Convert bounding boxes from [x,y,w,h] format to [x1,y1,x2,y2] format.

    Args:
        boxes (np.ndarray): Bounding boxes in [x,y,w,h] format.

    Returns:
            np.ndarray: Bounding boxes in [x1,y1,x2,y2] format.
    """
    # boxes: (N,4) -> [x,y,w,h] (center format) -> [x1,y1,x2,y2]
    x, y, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    x1 = x - w / 2.0
    y1 = y - h / 2.0
    x2 = x + w / 2.0
    y2 = y + h / 2.0
    return np.stack([x1, y1, x2, y2], axis=1)
