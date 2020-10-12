# Python EnOcean #

A Python library for reading and controlling [EnOcean](http://www.enocean.com/) devices.

This is a branch of the (unmaintained?) work of [kipe](https://github.com/kipe/enocean.git), which started as a part of [Forget Me Not](http://www.element14.com/community/community/design-challenges/forget-me-not) design challenge @ [element14](http://www.element14.com/).

## Install ##

If not installed already, install [pip](https://pypi.python.org/pypi/pip) by running

`sudo apt-get install python-pip`

After pip is installed, install the module by running

`sudo pip install py-enocean` (or `sudo pip install git+https://github.com/bakkerv/py-enocean.git`)

After this, it's just a matter of running `enocean_example.py` and pressing the
learn button on magnetic contact or temperature switch or pressing the rocker switch.

You should be displayed with a log of the presses, as well as parsed values
(assuming the sensors are the ones provided in the [EnOcean Starter Kit](https://www.enocean.com/en/enocean_modules/esk-300)).

The example script can be stopped by pressing `CTRL+C`
