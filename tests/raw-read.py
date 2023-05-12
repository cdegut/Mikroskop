from matplotlib import pyplot as plt
import picamraw

raw_bayer = picamraw.PiRawBayer(
    filepath='/home/pi/microscope_data/test.jpg',
    camera_version=picamraw.PiCameraVersion.V2,
)

plt.imshow(raw_bayer.to_rgb())