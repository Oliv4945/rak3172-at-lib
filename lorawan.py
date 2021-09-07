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
