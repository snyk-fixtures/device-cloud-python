"""
This module contains the Relay class which is a secure way to pipe data to a
local socket connection. This is useful for Telnet which is not secure by
default.
"""

import select
import socket
import ssl
import threading
import websocket

CONNECT_MSG = "CONNECTED-129812"

class Relay(object):
    """
    Class for establishing a secure pipe between a cloud based websocket and a
    local socket. This is useful for things like Telnet which are not secure to
    use remotely.
    """

    def __init__(self, wsock_host, sock_host, sock_port, secure=True,
                 log_func=None):
        """
        Initialize a relay object for piping data between a websocket and a
        local socket
        """

        self.wsock_host = wsock_host
        self.sock_host = sock_host
        self.sock_port = sock_port
        self.secure = secure
        self.log = log_func

        self.running = False
        self.thread = None
        self.lsock = None
        self.wsock = None

    def loop(self):
        """
        Main loop that pipes all data from one socket to the next. The websocket
        connection is established first so this is also where the local socket
        connection will be started when a specific string is received from the
        Cloud
        """

        while self.running is True:
            # Continuously receive data from each socket and send it through the
            # other
            socket_list = [self.wsock]
            if self.lsock:
                socket_list.append(self.lsock)
            read_sockets, _ws, _es = select.select(socket_list, [], [], 1)
            for sock in read_sockets:
                if sock == self.wsock:
                    try:
                        data_in = sock.recv()
                    except websocket.WebSocketConnectionClosedException:
                        self.running = False
                        break
                    if data_in:
                        if self.lsock:
                            self.lsock.send(data_in)
                        elif data_in == CONNECT_MSG:
                            # If the local socket has not been established yet,
                            # and we have received the connection string, start
                            # local socket.
                            try:
                                self.lsock = socket.socket(socket.AF_INET,
                                                           socket.SOCK_STREAM)
                                self.lsock.connect((self.sock_host,
                                                    self.sock_port))
                            except socket.error:
                                self.running = False
                                log_msg = "Failed to open local socket"
                                if self.log:
                                    self.log(log_msg)
                                else:
                                    print log_msg
                                break

                            log_msg = "Local socket successfully opened"
                            if self.log:
                                self.log(log_msg)
                            else:
                                print log_msg
                    else:
                        self.running = False
                        break
                elif self.lsock and sock == self.lsock:
                    data_in = sock.recv(4096)
                    if data_in:
                        self.wsock.send_binary(data_in)
                    else:
                        self.running = False
                        break
        if self.lsock:
            self.lsock.close()
            self.lsock = None
        self.wsock.close()
        self.wsock = None
        log_msg = "Sockets Closed"
        if self.log:
            self.log(log_msg)
        else:
            print log_msg

    def start(self):
        """
        Establish the websocket connection and start the main loop
        """

        if not self.running:
            self.running = True

            sslopt = {}
            if not self.secure:
                sslopt["cert_reqs"] = ssl.CERT_NONE

            # Connect websocket to Cloud
            self.wsock = websocket.WebSocket(sslopt=sslopt)
            try:
                self.wsock.connect(self.wsock_host)
            except ssl.SSLError as error:
                self.running = False
                self.wsock.close()
                self.wsock = None
                log_msg = "Failed to open Websocket"
                if self.log:
                    self.log(log_msg)
                else:
                    print log_msg
                raise error

            log_msg = "Websocket Opened"
            if self.log:
                self.log(log_msg)
            else:
                print log_msg

            self.thread = threading.Thread(target=self.loop)
            self.thread.start()

        else:
            raise RuntimeError("Relay is already running!")

    def stop(self):
        """
        Stop piping data between the two connections and stop the loop thread
        """

        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

