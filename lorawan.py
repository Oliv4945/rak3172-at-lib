from rak3172 import RAK3172
import sys

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

    device = RAK3172(
        serial_port=port, network_mode=RAK3172.NETWORK_MODES.LORAWAN, verbose=True
    )
    # device.joineui = "0102030405060708"
    # device.appkey = "11111111111111111111111111111113"

    # Display device informations
    print(f"Module devEUI: 0x{device.deveui}")
    print(f"Module joinEUI: 0x{device.joineui}")
    print(f"Module AppKey: 0x{device.appkey}")

    # Join the network
    device.join()
    while device.join_status() is not RAK3172.JOIN_STATUS.JOINED:
        False
    print("Device has joined the network")

    # Send a payload
    device.send_payload(2, b"FEED")
