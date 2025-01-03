# microcontrol
Software for the microscope
Works on raspberypi os bookworm,

# Raspbery pi config in /boot/firmware/config.txt
## I2C
```
# activate I2C interface
dtparam=i2c_arm=on
# Clock stretching by slowing down to 10KHz
dtparam=i2c_arm_baudrate=10000
```
## Screen configuration
for MPI7002, 7" 1024x600 touch screen; change:
```
dtoverlay=vc4-kms-v3d
```
to
```
dtoverlay=vc4-fkms-v3d
```
and at the end add:
```
# Allow for 1024x600 resolution do not add if using different screen
hdmi_group=2
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=1
```




# Package needed
upgrade pip and install the needed packages:
```
pip install --upgrade pip setuptools wheel smbus2 customtkinter packaging opencv-python --break-system-packages
sudo apt install python3-rpi-lgpio
```

# Misc
Strongly suggest to increase the size of the Swap file

```
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```
change:
```
CONF_SWAPSIZE=100
```
to
```
CONF_SWAPSIZE=2048
```
```
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

![Visit Stats](https://widgetbite.com/stats/cdegut)
