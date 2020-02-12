# Silencer 0.3.1

Push to talk functionality with top bar indicator for Ubuntu.

## Prerequisites

Install required dependencies.

```shell script
pip3 install pynput
sudo apt install gir1.2-appindicator3-0.1
```

## Usage
Using python directly:
```shell script
python3 silencer.py
```
Or using as executable:
```shell script
./silencer.py
```

**If you want to close the terminal without closing Silencer:**
```shell script
nohup silencer.py &
```
