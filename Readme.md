# Content
This is a quick hacked library to evaluate RAK3172 AT firmware thanks to
the RAK3272S breakout board.  
Lot of parts can be optimized but it is as far as I went in few dozens of minutes, PR are welcome ;-)

# Implemented features

Currently implemented properties:

* Set/Get `appkey`
* Get `deveui`, set is still TODO
* Set/Get `joineu` (`appeui` in loRaWAN 1.0.2 terminology)
* Set `network_mode`: `NETWORK_MODES.P2P` or `NETWORK_MODES.OTAA`
* Set/Get `verbose` mode to display all serial communications

functions:

* `join`: Join a LoRaWAN network
* `join_status`: Get join state
* `reset_soft`: Trigger a soft reset thanks to `ATZ` command
* `send_command`: Send an arbitrary AT command
* `send_payload`: Send a LoRaWAN payload. `payload` must be of `byte` type
* `status`: Return device status, mostly to check UART connectivity

# Installation
Clone the project then install python dependancies

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Usage
Find the serial port then pass it as parameter to the script, ex:

```
python lorawan.py /dev/ttyS20
```

# Project files

`lorawan.py` is an example file, it:

* Instanciate the RAK3172 object
* Set JoinEui (AppEui) and AppKey if required
* Display the EUIs
* Join
* Send a message!

`rak3172.py` is the class containing the RAK3172 object and its methods.

