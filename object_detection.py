import os
import time
import cv2
import numpy as np


class ObjectDetection:
    def __init__(self):
        PROJECT_PATH = os.path.abspath(os.getcwd())
        MODELS_PATH = os.path.join(PROJECT_PATH, "models")

        self.MODEL = cv2.dnn.readNet(
            os.path.join(MODELS_PATH, "yolov3.weights"),
            os.path.join(MODELS_PATH, "yolov3.cfg")
        )

        self.CLASSES = []
        with open(os.path.join(MODELS_PATH, "coco.names"), "r") as f:
            self.CLASSES = [line.strip() for line in f.readlines()]

        # Waste classification mapping
        self.WASTE_TYPES = {
            "biodegradable": ["apple" , "person" ,  "banana", "orange", "vegetable", "food"],
            "non-biodegradable": ["bottle" , "cell phone" , "remote" , "plastic", "can", "bag", "wrapper"],
            "chemical": ["battery", "chemical", "medicine", "oil", "paint"]
        }

        self.OUTPUT_LAYERS = [
            self.MODEL.getLayerNames()[i - 1] for i in self.MODEL.getUnconnectedOutLayers()
        ]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.CLASSES), 3))
        self.COLORS /= (np.sum(self.COLORS**2, axis=1)**0.5/255)[np.newaxis].T

        # Track recently detected objects
        self.recently_detected = {}  # Format: {object_name: last_detected_time}

    def get_waste_type(self, class_name):
        for waste_type, items in self.WASTE_TYPES.items():
            if class_name.lower() in items:
                return waste_type
        return "unknown"

    def detectObj(self, snap):
        height, width, channels = snap.shape
        blob = cv2.dnn.blobFromImage(
            snap, 1/255, (416, 416), swapRB=True, crop=False
        )

        self.MODEL.setInput(blob)
        outs = self.MODEL.forward(self.OUTPUT_LAYERS)

        class_ids = []
        confidences = []
        boxes = []
        detected_objects = []

        current_time = time.time()

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0]*width)
                    center_y = int(detection[1]*height)
                    w = int(detection[2]*width)
                    h = int(detection[3]*height)

                    x = int(center_x - w/2)
                    y = int(center_y - h/2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

                    class_name = self.CLASSES[class_id]
                    waste_type = self.get_waste_type(class_name)

                    # Check if the object was recently detected
                    if class_name in self.recently_detected:
                        # If the object was detected within the last 10 seconds, skip adding it to detected_objects
                        if current_time - self.recently_detected[class_name] < 10:
                            continue
                    else:
                        # Add the object to the recently detected list
                        self.recently_detected[class_name] = current_time
                        detected_objects.append((class_name, waste_type))

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.CLASSES[class_ids[i]])
                color = self.COLORS[i]
                cv2.rectangle(snap, (x, y), (x + w, y + h), color, 2)
                cv2.putText(snap, label, (x, y - 5), font, 2, color, 2)

        # Clean up old entries in recently_detected
        self.recently_detected = {
            k: v for k, v in self.recently_detected.items() if current_time - v < 10
        }

        return snap, detected_objects


class VideoStreaming(object):
    def __init__(self):
        super(VideoStreaming, self).__init__()
        self.VIDEO = cv2.VideoCapture(0)
        self.MODEL = ObjectDetection()
        self._preview = True
        self._flipH = False
        self._detect = False
        self._exposure = self.VIDEO.get(cv2.CAP_PROP_EXPOSURE)
        self._contrast = self.VIDEO.get(cv2.CAP_PROP_CONTRAST)
        self.detected_objects = []

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, value):
        self._preview = bool(value)

    @property
    def flipH(self):
        return self._flipH

    @flipH.setter
    def flipH(self, value):
        self._flipH = bool(value)

    @property
    def detect(self):
        return self._detect

    @detect.setter
    def detect(self, value):
        self._detect = bool(value)

    @property
    def exposure(self):
        return self._exposure

    @exposure.setter
    def exposure(self, value):
        self._exposure = value
        self.VIDEO.set(cv2.CAP_PROP_EXPOSURE, self._exposure)

    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, value):
        self._contrast = value
        self.VIDEO.set(cv2.CAP_PROP_CONTRAST, self._contrast)

    def show(self):
        while(self.VIDEO.isOpened()):
            ret, snap = self.VIDEO.read()
            if self.flipH:
                snap = cv2.flip(snap, 1)

            if ret == True:
                if self._preview:
                    if self.detect:
                        snap, self.detected_objects = self.MODEL.detectObj(snap)
                    else:
                        self.detected_objects = []

                frame = cv2.imencode(".jpg", snap)[1].tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(0.01)

            else:
                break
        print("off")