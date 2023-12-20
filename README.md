# microcontrol
Software for the microscope
Works on raspberypi os bookworm,
As of January 2024, there is a bug that provoke display crash if using wayland, 
Need to back to X11 using raspi-config

# Raspbery pi config in /boot/config.txt
```
# activate I2C interface
dtparam=i2c_arm=on
# Clock stretching by slowing down to 10KHz
dtparam=i2c_arm_baudrate=10000
```

# Package needed
upgrade pip and install the needed packages:
```
pip install --upgrade pip setuptools wheel smbus2 customtkinter packaging opencv-python --break-system-packages
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
