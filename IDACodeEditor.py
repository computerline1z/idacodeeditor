
# threading
import threading

# socket
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.netutil
import tornado.web
import socket
import json
import idaapi
import ida_nalt
import idc
# idaapi
from idaapi import *
from idc import *
import ida_kernwin, ida_diskio, ida_idaapi
import os, inspect, sys
import asyncio
import PyQt5
from PyQt5 import QtCore, QtGui
import webbrowser
PORT = 8000
HOST = "127.0.0.1"
URL = "127.0.0.1:8000"
def is_ida_version(requested):
    """Checks minimum required IDA version."""
    rv = requested.split(".")
    kv = ida_kernwin.get_kernel_version().split(".")

    count = min(len(rv), len(kv))
    if not count:
        return False

    for i in list(range(count)):
        if int(kv[i]) < int(rv[i]):
            return False
    return True

def get_items():
    keywords = set()
    subdir = ""
    if is_ida_version("7.5"):
        subdir, _, _, _, _ = sys.version_info
    pydir = ida_diskio.idadir(os.path.join("python", str(subdir)))
    for mod_name in os.listdir(pydir):
        if mod_name.endswith(".py"):
            mod_name, _ = os.path.splitext(mod_name)
            if mod_name not in ["init", "idaapi"]:
                mod = __import__(mod_name)
                keywords.add(mod_name)
                for sym_name, obj in inspect.getmembers(mod):
                    keywords.add(mod_name + "." + sym_name)
    return list(keywords)
                        
class Worker(PyQt5.QtCore.QEvent):
    def __init__(self, func, *args):
        super(Worker, self).__init__(0)
        self.func = func

    def __del__(self):
        self.func()


def execute_in_main_thread(func):
    lock = threading.Lock()

    def _handler():
        lock.acquire()
        worker = Worker(lambda: (lock.release(), func()))
        PyQt5.QtCore.QCoreApplication.postEvent(PyQt5.QtWidgets.qApp, worker)

    _handler()
    PyQt5.QtCore.QCoreApplication.processEvents()
    lock.acquire()
    lock.release()

def WriteFileScript(code):
    
    try:
        # ida dir
        path_ida = idaapi.idadir("plugins\\IDACodeEditor")

        # Write file folder 
        file = open(path_ida + "\\code.py", "w")
        file.write(code)    # write
        file.close()        # close

        # Execute Script
        execute_in_main_thread(ExecuteFileScript)
    except:
        print ("[ERROR] Error Write File")


def ExecuteFileScript():
    
    g = globals()

    try:
    
        # ida dir
        path_ida = idaapi.idadir("plugins\\IDACodeEditor")

        # Execute
        IDAPython_ExecScript(path_ida + "\\code.py", g)

    except:
        print ("[ERROR] Error Execute Script")


keywords = get_items()

class WSHandler(tornado.websocket.WebSocketHandler):
    
    def get_compression_options(self):
        return {'compression_level':5, 'mem_level':5}
    
    def open(self):
        cmd = {
            'action' : 'intelisence',
            'payload' : keywords
        }
        self.write_message(json.dumps(cmd))
        msg('Websocket Client Connected !')
    
    def on_message(self, message):
        #print ("Websocket Client Send Command!")
        if (message == 'ping'):
            self.write_message('pong')
        else:
            WriteFileScript(message)

    def check_origin(self, origin):
        return True

class MainHandler(tornado.web.RequestHandler):
    
    def initialize(self, address, title):
        self.address = address
        self.title = title
    
    def get_template_path(self):
        return idaapi.idadir("plugins\\IDACodeEditor\\public")
        
    def get(self):
        self.render("index.html", title=self.title, address=self.address)


class StartServer(threading.Thread):
    def __init__(self, sockets, title):
        super(StartServer, self).__init__()
        self.sockets = sockets
        self.title = title
    def run(self):
        print ("IDA Code Editor | Dev Bym24v")
        #myIP = socket.gethostbyname(socket.gethostname())
        # bind address
        self.address = "%s:%s" % (HOST, self.sockets[0].getsockname()[1])
        
        application = tornado.web.Application([
            (r'/', MainHandler, dict(address=self.address, title=self.title)),
            (r'/css/(.*)', tornado.web.StaticFileHandler, {"path": idaapi.idadir("plugins\\IDACodeEditor\\public\\css")}),
            (r'/js/(.*)', tornado.web.StaticFileHandler, {"path": idaapi.idadir("plugins\\IDACodeEditor\\public\\js")}),
            (r'/ws', WSHandler)
        ])
        asyncio.set_event_loop(asyncio.new_event_loop())
        server = tornado.httpserver.HTTPServer(application)
        server.add_sockets(self.sockets)
        tornado.ioloop.IOLoop.instance().start()


class IDACodeEditor(idaapi.plugin_t):
    
    # settings plugin
    flags = idaapi.PLUGIN_FIX
    comment = "IDA Code Editor"
    help = "IDA Code Editor"
    wanted_name = "IDA Code Editor"
    wanted_hotkey = ''

    # init
    def init(self):
        self.is_server_start = False
        print("[IDACodeEditor] Loading ...")
        if not self.is_server_start:
            sockets = tornado.netutil.bind_sockets(0, '127.0.0.1')
            server = StartServer(sockets, title=ida_nalt.get_root_filename())
            server.daemon = True
            server.start()
            self.URL = "%s:%s" % (HOST, sockets[0].getsockname()[1])
            print("[IDACodeEditor] Server started %s." % self.URL)
            self.is_server_start = True
        return idaapi.PLUGIN_KEEP

    # Run new Thread
    def run(self, arg):
        print("[IDACodeEditor] Server is running !")
        webbrowser.register('chrome',
        	None,
        	webbrowser.BackgroundBrowser("C://Program Files (x86)//Google//Chrome//Application//chrome.exe"))
        webbrowser.get('chrome').open_new('http://' + self.URL + '/')

    def term(self):
        if self.is_server_start:
            tornado.ioloop.IOLoop.instance().stop()
            self.is_server_start = False
        pass

def PLUGIN_ENTRY():
    return IDACodeEditor()

if __name__ == "__main__":
    PLUGIN_ENTRY()