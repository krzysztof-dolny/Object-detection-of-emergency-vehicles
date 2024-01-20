from ultralytics import YOLO

# Trening modelu
model = YOLO('yolov8s.pt')
training_results = model.train(
    data='config.yaml',
    epochs=186,
    imgsz=320,
    batch=10,
    optimizer='Adam')

# Wczytanie wytrenowanego modelu
model = YOLO('C:/Users/krzys/Desktop/projekt_yolo/runs/detect/train/weights/best.pt')

# Validacja
metrics = model.val(
    data='config.yaml',
    imgsz=320,
    batch=10)

# Test
source='C:/Users/krzys/Desktop/projekt_yolo/data/images/test'
test_results = model(
    source,
    imgsz=320,
    conf=0.6,
    save=True,
    save_txt=True,
    max_det=5)

