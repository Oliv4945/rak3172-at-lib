from threading import Event
from rak3172 import RAK3172
import signal
import sys


class STATES:
    JOINING = 0
    JOINED = 1
    SEND_DATA = 2
    SLEEP = 3


device = None
state = None


def events(type, parameter):
    global state

    if type == RAK3172.EVENTS.JOINED:
        state = STATES.JOINED
        print("EVENT - Joined")
    elif type == RAK3172.EVENTS.SEND_CONFIRMATION:
        print(f"EVENT - Confirmed: {parameter}")
    else:
        print("EVENT - Unknown event {type}")


def handler_timeout_tx(signal, frame):
    global state
    state = STATES.SEND_DATA


def handler_sigint(signal, frame):
    device.close()
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "\n\n================================================================\nMissing argument! Usage:"
        )
        print("> python3 lorawan.py /dev/ttyUSB0")
        sys.exit(
            "Leaving now\n================================================================\n\n"
        )
    port = str(sys.argv[1])

    # Prepare signal management
    signal.signal(signal.SIGALRM, handler_timeout_tx)
    signal.signal(signal.SIGINT, handler_sigint)

    device = RAK3172(
        serial_port=port,
        network_mode=RAK3172.NETWORK_MODES.LORAWAN,
        verbose=True,
        callback_events=events,
    )
    # device.deveui = "0807060504030201"
    # device.joineui = "0102030405060708"
    # device.appkey = "11111111111111111111111111111113"

    # Display device informations
    print(f"Module devEUI: 0x{device.deveui}")
    print(f"Module joinEUI: 0x{device.joineui}")
    print(f"Module AppKey: 0x{device.appkey}")

    # Join the network
    device.join()
    state = STATES.JOINING

    while True:
        if state == STATES.JOINED:
            print("Device has joined the network")
            state = STATES.SEND_DATA
        elif state == STATES.SEND_DATA:
            # Send a payload
            device.send_payload(2, b"FEED")
            signal.alarm(10)
            state = STATES.SLEEP
        elif state == STATES.SLEEP:
            pass
