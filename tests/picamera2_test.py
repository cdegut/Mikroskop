from picamera2 import Picamera2, Preview
import time
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.QT)
print(picam2.camera_controls)
picam2.start()
#picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0, 'ColourGains': })
picam2.controls.ExposureTime = 10000
picam2.controls.AwbEnable = False
picam2.controls.ColourGains = 1.0, 0.3

while True:
    time.sleep(1)
#picam2.capture_file("test.jpg")