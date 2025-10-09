# Python EnOcean #

[![Linting And Testing Status](https://github.com/topic2k/enocean4ha/actions/workflows/lint_and_test.yml/badge.svg?branch=main)](https://github.com/topic2k/enocean4ha/actions/workflows/lint_and_test.yml)
[![Coverage Status](https://coveralls.io/repos/github/topic2k/enocean4ha/badge.svg?branch=main)](https://coveralls.io/github/topic2k/enocean4ha?branch=main)
[![PyPi](https://img.shields.io/pypi/v/enocean4ha?logo=pypi&logoColor=959DA5)](https://pypi.org/project/enocean4ha/)


A Python library for reading and controlling [EnOcean](http://www.enocean.com/) devices.

It started as a part of the [Forget Me Not](http://www.element14.com/community/community/design-challenges/forget-me-not)
design challenge @ [element14](http://www.element14.com/).

<sub>This fork was created, because the [original repo](https://github.com/kipe/enocean) seems to be inactive, and i needed
to add EEPs to make some devices usable in [Home Assistant](https://www.home-assistant.io/).</sub>



## Install ##

If not installed already, install [pip](https://pypi.python.org/pypi/pip) by running

`sudo apt-get install python-pip`

After pip is installed, install the module by running

`sudo pip install enocean4ha` (or `sudo pip install git+https://github.com/topic2k/enocean4ha.git` if you want the "bleeding edge").

After this, it's just a matter of running `enocean_example.py` and pressing the
learn button on magnetic contact or temperature switch or pressing the rocker switch.

You should be displayed with a log of the presses, as well as parsed values
(assuming the sensors are the ones provided in the [EnOcean Starter Kit](https://www.enocean.com/en/enocean_modules/esk-300)).

The example script can be stopped by pressing `CTRL+C`

---

