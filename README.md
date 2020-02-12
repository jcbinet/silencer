# Silencer 0.3.3

Push to talk functionality with top bar indicator for Ubuntu.

## Prerequisites

Install required dependencies.

```shell script
pip3 install pynput
sudo apt install gir1.2-appindicator3-0.1
```

## Config
Configurations are stored in `silencer-config.json`:

`keybind:` key for mic

`hold_to_talk:` Hold to talk mode | Toggle mode

`sound_card_id:` Sound card id of mic

Default values are:
```json
{
  "keybind": "f8",
  "hold_to_talk": true,
  "sound_card_id": 1
}
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
