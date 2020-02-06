# Silencer 0.1.0

Push to talk functionality with top bar indicator for Ubuntu using Gtk AppIndicator3 and amixer.

## Prerequisites
Install required dependencies.

```shell script
pip3 install pynput
sudo apt install gir1.2-appindicator3-0.1
```

## Usage

```shell script
usage: silencer.py [-h] [-k K] [-c C] [--no-hold]

optional arguments:
  -h, --help  show this help message and exit
  -k K        Toggle key
  -c C        Sound card id
  --no-hold   No need to hold key bind to talk
```
