# Author: Oliv4945
# AT commands documentation
# https://docs.rakwireless.com/Product-Categories/WisDuo/RAK3172-Module/AT-Command-Manual/

import serial
import sys
import time


class RAK3172:
    serial = None

    class NETWORK_MODES:
        P2P = 0
        LORAWAN = 1

    class JOIN_MODES:
        ABP = 0
        OTAA = 1

    class JOIN_STATUS:
        NOT_JOINED = 0
        JOINED = 1

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

    @property
    def network_mode(self):
        return self.__network_mode

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
    def appkey(self):
        ans = self.send_command("AT+APPKEY=?")
        if ans[-2] != "OK":
            print("ERROR - Unable to get APPKEY")
            exit()
        return ans[0].upper()

    @appkey.setter
    def appkey(self, appkey):
        ans = self.send_command(f"AT+APPKEY={appkey}")
        if ans[-2] != "OK":
            print("ERROR - Unable to set AppKEY")
            exit()
        # RAK3172 needs to be restarted to take it into account
        self.reset_soft()

    @property
    def deveui(self):
        ans = self.send_command("AT+DEVEUI=?")
        if ans[-2] != "OK":
            print("ERROR - Unable to get devEUI")
            exit()
        return ans[0].upper()

    # TODO - Implement devEUI setter

    @property
    def joineui(self):
        ans = self.send_command("AT+APPEUI=?")
        if ans[-2] != "OK":
            print("ERROR - Unable to get joinEUI")
            exit()
        return ans[0].upper()

    @joineui.setter
    def joineui(self, joineui):
        ans = self.send_command(f"AT+APPEUI={joineui}")
        if ans[-2] != "OK":
            print("ERROR - Unable to set joinEUI")
            exit()
        # RAK3172 needs to be restarted to take it into account
        self.reset_soft()

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

    def join(self):
        ans = self.send_command(f"AT+NJM={RAK3172.JOIN_MODES.OTAA}")
        if ans[-2] != "OK":
            print("ERROR - Unable to get join mode")
        ans = self.send_command("AT+JOIN=1:0:8:0")
        if ans[-2] != "OK":
            print("ERROR - Unable to join")

    def join_status(self):
        ans = self.send_command(f"AT+NJS=?")
        if ans[-2] != "OK":
            print("ERROR - Unable to get join status")
        return int(ans[0])

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

    def send_payload(self, fport, payload, confirmed=False):
        # TODO - Implement confirm messages
        ans = self.send_command(f'AT+SEND={fport}:{payload.decode("ASCII")}')
        if ans[-2] != "OK":
            print("ERROR - Unable to send payload")

    def status(self):
        ans = self.send_command("AT")
        if ans[-2] == "OK":
            return True
        else:
            return False
