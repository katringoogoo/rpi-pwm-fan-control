# rpi-pwm-fan-control

## Motivation
This Python script was created for the purpose to control a PWM FAN Noctua NF-A4x20 5V, using Raspberry Pi 4B hardware features.

While the original script uses WiringPi this script rebuilds everything on top of gpiozero.

* It is set to use Hardware PWM value clock as 25Khz that was specified by Intel (c.f. “4-Wire Pulse Width Modulation (PWM) Controlled Fans”, Intel Corporation September 2005, revision 1.3). 
* To read the FAN speed a DigitalInputDevice is used that counts the falling flanks. 
* The temperature is directly read from the linux file system
* The input values are then used to update an PID controller and the output is directly used to set the PWM duty cycle value

## Wiring
- Set PWM pin to control the FAN (e.g. GPIO6)
- Set TACHO pin to read FAN speed (e.g. GPIO12)
- The other 2 fan pins can be directly connected to 5V & GND pins
- CPU usage stay between 1% and 2%, because it needs to process the tachometer interruption routine

## Dependencies
* [Python 3](https://www.python.org/download/releases/3.0/) - The script interpreter
* [GPIO Zero](https://gpiozero.readthedocs.io/) - Control Hardware features of Rasbberry Pi

## Documentations
* [Noctua white paper](https://noctua.at/pub/media/wysiwyg/Noctua_PWM_specifications_white_paper.pdf) - Noctua PWM specifications white paper

## How to use
```sh
$ git clone https://github.com/katringoogoo/rpi-pwm-fan-control.git
$ cd rpi-pwm-fan-control
$ pip3 install -r requirements.txt
$ python3 ./rpi-pwmfan.py
```
