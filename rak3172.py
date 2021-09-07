# Author: Oliv4945
# AT commands documentation
# https://docs.rakwireless.com/Product-Categories/WisDuo/RAK3172-Module/AT-Command-Manual/

import serial
import sys


class RAK3172:
    serial = None

    class NETWORK_MODES:
        P2P = 0
        LORAWAN = 1

    def __init__(self, serial_port, network_mode, verbose=False):
        self.serial_port = serial_port
        self.verbose = verbose

        # Open serial port
        try:
            self.serial = serial.serial_for_url(serial_port, 9600, timeout=0.5)
        except serial.SerialException as e:
            sys.exit("/!\ Yo Dukie! Port not found! Aborting.")
        self.serial.reset_input_buffer()

        # Check chip presence
        if self.status() is not True:
            print("ERROR - Unable to detect chip")
            exit()

        # Ensure network mode
        self.network_mode = network_mode

    @network_mode.setter
    def network_mode(self, network_mode):
        ans = self.send_command("AT+NWM=?")
        if ans[-2] != "OK":
            print("ERROR - Unable to check network mode")
            exit()
        if int(ans[0]) != network_mode:
            ans = self.send_command(f"AT+NWM={network_mode}")
        self.__network_mode = network_mode

    @property
    def verbose(self):
        return self.__verbose

    @verbose.setter
    def verbose(self, verbose):
        self.__verbose = verbose

    @property
    def serial_port(self):
        return self.__serial_port

    @serial_port.setter
    def serial_port(self, port):
        self.__serial_port = port

    def reset_soft(self):
        ans = self.send_command(f"ATZ")
        # Give some time to the device to restart
        time.sleep(1.0)
        self.serial.flushInput()

    def send_command(self, cmd, ignore=False):
        self.serial.write(cmd.encode("ASCII") + b"\r\n")

        if self.verbose is True:
            print(f"-> {cmd.upper()}")

        self.serial.flush()
        b = b""
        if ignore == False:
            received = self.serial.read(300)
            received = received.decode("ASCII").split("\r\n")
            if self.verbose is True:
                print(f"<- {[x.upper() for x in received]}")
            return received
        else:
            return None

    def status(self):
        ans = self.send_command("AT")
        if ans[-2] == "OK":
            return True
        else:
            return False
