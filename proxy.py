import subprocess
import argparse
import signal
import time
import os

from Xlib import display
from Xlib import X, Xatom, XK
from Xlib.error import XError
from multiprocessing import Process, Manager

mg = Manager()
killed = mg.Value('i', 0)

class KeysProxy:
    def __init__(self, key, modifier, cmd):
        self.d = display.Display()

        self.last_wnd = None

        self.root = self.d.screen().root
        self.tree = self.root.query_tree()
        self.detect_window()
        self.key = self.char_to_key(key)
        self.modifier = modifier
        self.cmd = cmd

    def char_to_key(self, s):
        keysym = XK.string_to_keysym(s)
        keycode = self.d.keysym_to_keycode(keysym)
        return keycode

    def get_active_window(self):
        active = self.d.get_input_focus().focus
        name = active.get_wm_name()
        wnd = active.id
        last = self.last_wnd
        if wnd != last:
            self.last_wnd = wnd
    
        return active, last != wnd # window: Window, changed: bool

    def detect_window(self):
        w, _ = self.get_active_window()
        changed = False
        while not changed:
            w, changed = self.get_active_window()
        self.window = w

    def get_window_pid(self, window) -> str:
        atom = self.d.get_atom("_NET_WM_PID")
        pid_property = window.get_full_property(atom, X.AnyPropertyType)
        if pid_property:
            pid = pid_property.value[-1]
            return pid
        else:
            raise Exception("pid_property was None")
    
    def grab_key(self):
        self.window.change_attributes(event_mask=X.KeyPressMask)
        self.window.grab_key(self.key, self.modifier, True, X.GrabModeAsync, X.GrabModeAsync)
    
    def ungrab_key(self):
        self.window.change_attributes(event_mask=0)
        self.window.ungrab_key(self.key, self.modifier)

    def run_cmd(self):
        subprocess.Popen(self.cmd, shell=True)

    def handle_event(self, event):
        if event.type != X.KeyPress:
            return
        keycode = event.detail
        modifiers = event.state
        if keycode == self.key and modifiers == self.modifier:
            self.run_cmd()
            self.d.send_event(self.window, event, propagate=True)
            self.d.sync()
    
    def run_proxy(self):
        self.grab_key()
        while True:
            if killed.value:
                break
            if self.d.pending_events():
                self.handle_event(self.d.next_event())
            time.sleep(0.01)

def process_run_and_monitor(cmd):
    p = subprocess.Popen(cmd, shell=True)
    p.wait()
    killed.value = 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', '-k', required=True, help='Key to capture (examples: S, M, etc.)')
    parser.add_argument('--modifier', '-m', required=True, help='Modifier to capture (examples: shift, ctrl, alt)')
    parser.add_argument('--cmd', '-c', required=True, help='Shell command to run on captured key')
    parser.add_argument('program', help='Program to run')
    args = parser.parse_args()
    program = args.program
    key = args.key
    assert len(key) == 1, 'Key should be just one character!'
    if args.modifier.lower() == 'shift':
        modifier = X.ShiftMask
    elif args.modifier.lower() == 'alt':
        modifier = X.AltMask
    elif args.modifier.lower() == 'ctrl':
        modifier = X.ControlMask
    else:
        raise Exception('Modifier can be one of the following values only: shift, ctrl, alt')
    cmd = args.cmd

    p = Process(target=process_run_and_monitor,args=(program,))
    p.daemon = True
    p.start()
    proxy = KeysProxy(key, modifier, cmd)
    proxy.run_proxy()

if __name__ == '__main__':
    main()
