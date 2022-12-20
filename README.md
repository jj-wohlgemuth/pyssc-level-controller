# pyssc-level-controller

https://user-images.githubusercontent.com/52459869/208654225-f41d325c-9d07-4cfa-9168-5cbdcaa6533b.mov

## Hardware
For this project I used:
* A Raspberry Pi
* AFC-113 I2C Display-Driver
* A HD44780 1602 LCD
* A KY-040 Rotary Encoder

You will find countless helpful tutorials on how to hook those components up.

## Controller Setup

* Install Linux on your controller (I used Raspbian)
* Make sure you have a version of Python 3 installed
* Clone or copy this repo to the Linux machine
* Create a setup.json file in the controller folder. Refer to the [pyssc documentation](https://github.com/jj-wohlgemuth/pyssc) for more information
* Open a terminal on your Linux machine and change to the level controller folder
* Run ```pip install -r requirements.txt``` (for that you need an internet connection)
* Run ```sudo nano /etc/rc.local```
* Add the following two lines and save the file
```
cd <PATH_TO_FOLDER>
sudo python3 main.py &
```
* Reboot your Linux machine




