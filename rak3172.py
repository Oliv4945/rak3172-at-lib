# Author: Oliv4945
# AT commands documentation
# https://docs.rakwireless.com/Product-Categories/WisDuo/RAK3172-Module/AT-Command-Manual/

import serial
import sys
import threading
import time


class RAK3172:
    serial = None
    STATUS_CODES = ["OK", "AT_ERROR", "AT_PARAM_ERROR", "AT_BUSY_ERROR"]

    class NETWORK_MODES:
        P2P = 0
        LORAWAN = 1

    class JOIN_MODES:
        ABP = 0
        OTAA = 1

    class JOIN_STATUS:
        NOT_JOINED = 0
        JOINED = 1

    class EVENTS:
        JOINED = 0
        SEND_CONFIRMATION = 1

    def __init__(self, serial_port, network_mode, verbose=False, callback_events=None):
        self.serial_port = serial_port
        self.verbose = verbose
        self.__callback_events = callback_events

        # Open serial port
        try:
            self.serial = serial.serial_for_url(serial_port, 9600)
        except serial.SerialException as e:
            sys.exit("/!\ Yo Dukie! Port not found! Aborting.")
        self.serial.reset_input_buffer()

        # Open RX thread
        self.thread_rx_handle = threading.Thread(target=self.thread_rx)
        self.data_received = threading.Event()
        self.thread_rx_ready = threading.Event()
        self.thread_rx_kill = threading.Event()
        self.thread_rx_handle.start()

        # Check chip presence
        if self.status() is not True:
            print("ERROR - Unable to detect chip")
            exit()

        # Ensure network mode
        self.network_mode = network_mode

    def thread_rx(self):
        self.thread_rx_ready.set()
        while not self.thread_rx_kill.is_set():
            rx = self.serial.read_until(b"\r\n").decode("ASCII").rstrip().upper()
            if not len(rx):
                # Drop empty lines
                continue
            self.thread_rx_ready.clear()
            if True:
                print(f"<- {rx}")
            if rx[0] == "+":
                if rx == "+EVT:JOINED":
                    self.__callback_events(RAK3172.EVENTS.JOINED, None)

                if rx.startswith("+EVT:SEND CONFIRMED"):
                    if rx == "+EVT:SEND CONFIRMED OK":
                        self.__callback_events(RAK3172.EVENTS.SEND_CONFIRMATION, True)
                    else:
                        self.__callback_events(RAK3172.EVENTS.SEND_CONFIRMATION, False)
            else:
                self.data_rx = rx
                self.data_received.set()
                time_start = time.time()
                while self.data_received.is_set():
                    # Wait for data to be processed or timeout
                    if time.time() > time_start + 0.1:
                        # Timeout, prepare for next RX
                        self.data_received.clear()
                        self.data_rx = ""
            self.thread_rx_ready.set()

    @property
    def network_mode(self):
        return self.__network_mode

    @network_mode.setter
    def network_mode(self, network_mode):
        status, data = self.send_command("AT+NWM=?")
        if status != "OK":
            print("ERROR - Unable to check network mode")
            sys.exit(1)
        if int(data) != network_mode:
            status, _ = self.send_command(f"AT+NWM={network_mode}")
            if status != "OK":
                print("ERROR - Unable to set network mode")
                sys.exit(1)
        self.__network_mode = network_mode

    @property
    def appkey(self):
        status, data = self.send_command("AT+APPKEY=?")
        if status != "OK":
            print("ERROR - Unable to get APPKEY")
            exit()
        return data

    @appkey.setter
    def appkey(self, appkey):
        status, _ = self.send_command(f"AT+APPKEY={appkey}")
        if status != "OK":
            print("status", status)
            print("ERROR - Unable to set AppKEY")
            exit()
        # RAK3172 needs to be restarted to take it into account
        self.reset_soft()

    @property
    def deveui(self):
        status, data = self.send_command("AT+DEVEUI=?")
        if status != "OK":
            print("ERROR - Unable to get devEUI")
            exit()
        return data

    @deveui.setter
    def deveui(self, deveui):
        status, _ = self.send_command(f"AT+DEVEUI={deveui}")
        if status != "OK":
            print("ERROR - Unable to set devEUI")
            exit()
        # RAK3172 needs to be restarted to take it into account
        self.reset_soft()

    @property
    def joineui(self):
        status, data = self.send_command("AT+APPEUI=?")
        if status != "OK":
            print("ERROR - Unable to get joinEUI")
            exit()
        return data

    @joineui.setter
    def joineui(self, joineui):
        status, _ = self.send_command(f"AT+APPEUI={joineui}")
        if status != "OK":
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

    def close(self):
        self.thread_rx_kill.set()

    def join(self):
        status, _ = self.send_command(f"AT+NJM={RAK3172.JOIN_MODES.OTAA}")
        if status != "OK":
            print("ERROR - Unable to set join mode")
        status, _ = self.send_command("AT+JOIN=1:0:8:0")
        if status != "OK":
            print("ERROR - Unable to join")

    def join_status(self):
        status, data = self.send_command(f"AT+NJS=?")
        if status != "OK":
            print("ERROR - Unable to get join status")
        return int(data)

    def reset_soft(self):
        self.send_command(f"ATZ", ignore=True)
        # Give some time to the device to restart
        time.sleep(1.0)
        self.serial.reset_input_buffer()

    def send_command(self, cmd, ignore=False):
        # Ensure case
        cmd = cmd.upper()
        # Clear RX buffer
        self.data_rx = []
        # Send command as soon as RX thread is available
        if not self.thread_rx_ready.wait(10):
            return None, None
        self.serial.write(cmd.encode("ASCII") + b"\r\n")
        self.serial.flush()

        if self.verbose is True:
            print(f"-> {cmd}")

        if not ignore:
            if self.data_received.wait(10):
                # Get data or status code
                data = self.data_rx
                self.data_received.clear()
                if data in RAK3172.STATUS_CODES:
                    return data, None
                # Already got data, only status code remaining
                if self.data_received.wait(10):
                    status = self.data_rx
                    self.data_received.clear()
                    return status, data

        return None, None

    def send_payload(self, fport, payload, confirmed=False):
        # TODO - Implement confirm messages
        status, _ = self.send_command(f'AT+SEND={fport}:{payload.decode("ASCII")}')
        if status != "OK":
            print("ERROR - Unable to send payload")

    def status(self):
        status, _ = self.send_command("AT")
        if status == "OK":
            return True
        else:
            return False
