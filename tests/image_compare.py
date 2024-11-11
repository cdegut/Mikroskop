import cv2
import numpy as np
from os import environ


## this avoid an error with CV2 and Qt, it clear all the env starting with QT_
#for k, v in environ.items():
#    if k.startswith("QT_") and "cv2" in v:
#        del environ[k]   

# Load the two images
image1 = cv2.imread('/home/microscope/microscope_data/accuracy_test-241111_1439/00000.png', cv2.IMREAD_GRAYSCALE)
image2 = cv2.imread('/home/microscope/microscope_data/accuracy_test-241111_1439/00001.png', cv2.IMREAD_GRAYSCALE)

# Ensure the images are the same size (resize if necessary)
if image1.shape != image2.shape:
    print("Images are not the same size. Resizing image2 to match image1.")
    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

# Use phase correlation to find the shift
shift = cv2.phaseCorrelate(np.float32(image1), np.float32(image2))

# Print the shift (translation in X and Y)
print(f"Translation in pixels (X, Y): {shift[0]}")

