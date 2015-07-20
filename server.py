#! /usr/bin/env python
import SocketServer, subprocess, sys 
from threading import Thread
import time
from evdev import InputDevice, list_devices, InputEvent, ecodes, UInput


HOST = '192.168.0.108'
PORT = 2000

''' Future capability to run commands '''
''' example: reply = pipe_command(my_unix_command, data)'''
def pipe_command(arg_list, standard_input=False):
    "arg_list is [command, arg1, ...], standard_input is string"
    pipe = subprocess.PIPE if standard_input else None
    subp = subprocess.Popen(arg_list, stdin=pipe, stdout=subprocess.PIPE)
    if not standard_input:
        return subp.communicate()[0]
    return subp.communicate(standard_input)[0]

def doKey(inputType, inputKey):
    ev = InputEvent(time.time(), 0, inputType, inputKey, 1)
    with UInput() as ui:
        ui.write_event(ev)
        ui.syn()

class SingleTCPHandler(SocketServer.BaseRequestHandler):
    "One instance per connection.  Override handle(self) to customize action."
    def handle(self):
        # self.request is the client connection
        while True:
            data = self.request.recv(1024)  # clip input at 1Kb
            print data
            if not data:
                break
            if 'exit' in data:
                break
            elif 'up' in data:
                doKey(ecodes.EV_KEY, ecodes.KEY_UP)

            
            reply = "{'success': True }"
            if reply is not None:
                self.request.send(reply)
        self.request.close()



class SimpleServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

if __name__ == "__main__":
    server = SimpleServer((HOST, PORT), SingleTCPHandler)
    # terminate with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
