# Raspbery pi config

These are specific configurations needed for the Raspbery Pi to work well with the microscope.

all these change need to be made in

## in /boot/firmware/config.txt

### I2C

*Mandatory change*

```bash
# activate I2C interface
dtparam=i2c_arm=on
# Clock stretching by slowing down to 10KHz
dtparam=i2c_arm_baudrate=10000
```

### Screen configuration

if using MPI7002, 7" 1024x600 touch screen; change:

```bash
dtoverlay=vc4-kms-v3d
```

to

```bash
dtoverlay=vc4-fkms-v3d
```

and at the end add:

```bash
# Allow for 1024x600 resolution do not add if using different screen
hdmi_group=2
hdmi_mode=87
hdmi_cvt 1024 600 60 6 0 0 0
hdmi_drive=1
```

## Packages to install

upgrade pip and install the needed packages:

```bash
pip install --upgrade pip setuptools wheel smbus2 customtkinter packaging opencv-python --break-system-packages
sudo apt install python3-rpi-lgpio
```

## Increase Swap size

Strongly suggest to increase the size of the Swap file:

run these two commands:

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
```

then change:

```bash
CONF_SWAPSIZE=100
```

to

```bash
CONF_SWAPSIZE=2048
```

And run again these:

```bash
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```
