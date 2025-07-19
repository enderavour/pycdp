from subprocess import Popen
import requests
from websockets.sync.client import connect
from time import sleep
import json
from base64 import b64decode
from .keys import HotKey, Key

class ChromeManager:
    def __init__(self, exec_path: str, user_profile_path: str, 
        terminate_on_end: bool, server_port: int = 9222):
            self.exec_path = exec_path
            self.port = server_port
            self.uprofile = user_profile_path
            self.finalized = terminate_on_end

    def start_session(self, *chromium_args):
        load_args = [
            self.exec_path, 
            f"--remote-debugging-port={self.port}", 
            f"--user-data-dir={self.uprofile}",
            *chromium_args
        ]
        self.inst = Popen(load_args)

    def init_ws_connection(self):
        basic_info_url = f"http://localhost:{self.port}/json"

        resp = requests.get(basic_info_url)
        self.ws_url = resp.json()[0]["webSocketDebuggerUrl"]
        self.conn = connect(self.ws_url)

    def screenshot(self, format: str) -> bytes:
        command = {
            "id": 1,
            "method": "Page.captureScreenshot",
            "params": {
                "format": format
            }
        }
        self.conn.send(json.dumps(command))
        response = json.loads(self.conn.recv())["result"]["data"]
        return b64decode(response)
    
    def navigate(self, url: str) -> dict:
        command = {
            "id": 2,
            "method": "Page.navigate",
            "params": {
                "url": url
            }
        }
        self.conn.send(json.dumps(command))
        response = json.loads(self.conn.recv())
        return response
    
    def send_key(self, key: Key, hotkey: HotKey = HotKey.Default):
        def send_event(event_type, key_code, modifiers):
            message = {
                "id": 3,
                "method": "Input.dispatchKeyEvent",
                "params": {
                    "type": event_type,
                    "windowsVirtualKeyCode": key_code,
                    "modifiers": modifiers
                }
            }
            self.conn.send(json.dumps(message))

        if hotkey != HotKey.Default:
            send_event("keyDown", hotkey.key_code, hotkey.value)

        send_event("keyDown", key.value, hotkey.value)
        send_event("keyUp", key.value, hotkey.value)

        if hotkey != HotKey.Default:
            send_event("keyUp", hotkey.key_code, 0)

    def execute_script(self, script: str) -> dict:
        command = {
            "id": 4,
            "method": "Runtime.evaluate",
            "params": {
                "expression": script,
                "returnByValue": True
            }
        }
        self.conn.send(json.dumps(command))
        response = json.loads(self.conn.recv())
        return response
    
    def scroll(self, pixels: int, behaviour = "smooth") -> dict:
        if behaviour not in ["smooth", "instant", "auto"]:
            return {}
        res = self.execute_script("""
            window.scrollTo({{
                top: {0},
                left: 0,
                behavior: '{1}'
            }});
        """.format(pixels, behaviour))
        print(res)
        return res

    def finalize(self):
        self.conn.close()
        self.inst.terminate()

    def __del__(self):
        if self.finalized:
            self.finalize()


