# rpi-pwm-fan-control

## Motivation
This Python script was created for the purpose to control a PWM FAN Noctua NF-A4x20 5V, using Raspberry Pi 4B hardware features.

While the original script uses WiringPi this script rebuilds everything on top of gpiozero.

* To read the FAN speed a DigitalInputDevice is used that counts the falling flanks. 
* Depending on the pin that is used for fan PWM control gpiozero uses hardware or software PWM (Hardware PWM is available on pins GPIO12, GPIO13, GPIO18, GPIO19)
* The temperature is directly read from the linux file system
* The input values are then used to update an PID controller
* The output of hte PID controller is mapped to the PWM range of the Noctua Fan (20% - 100%)

## Wiring
- Set PWM pin to control the FAN (e.g. GPIO12)
- Set TACHO pin to read FAN speed (e.g. GPIO6)
- The other 2 fan pins can be directly connected to 5V & GND pins
- CPU usage stays between 1% and 2% (if a higher pwm frequence is used it requires more processing power although it shouldn't)

## Dependencies
* [Python 3](https://www.python.org/download/releases/3.0/) - The script interpreter
* [GPIO Zero](https://gpiozero.readthedocs.io/) - Control Hardware features of Rasbberry Pi

## Documentations
* [Noctua white paper](https://noctua.at/pub/media/wysiwyg/Noctua_PWM_specifications_white_paper.pdf) - Noctua PWM specifications white paper

## How to use

```sh
git clone https://github.com/katringoogoo/rpi-pwm-fan-control.git
cd rpi-pwm-fan-control
pip3 install -r requirements.txt
./rpi-pwmfan.py
```

## Hardware PWM

In order be able to use Hardware PWM make sure that you connected the PWM pin of the fan to a hardware capable pin on the Raspberry Pi. 

Next install the pigpio library & daemon:

```sh
sudo apt-get install pigpio
sudo systemctl start pigpiod    # start the daemon
sudo systemctl enable pigpiod   # optional: autostart on startup
```

and start the script with the following arguments

```sh
./rpi-pwmfan.py --use-pigpio
```

Note: if you want to disable pigpiod again you have to stop the daemon with `sudo systemctl stop pigpiod`

More information is available on the pigpio [website](http://abyz.me.uk/rpi/pigpio/index.html)
