#!/usr/bin/env python3
#Nintendo DS FPS mousefix for linux - main GUI
#S.D.G.

import mouse
import keyboard
import pyautogui #For HUD detection and working around faults in the mouse and keyboard modules
import time
import queue
import threading
import tkinter as tk
from tkinter import messagebox as mb
import os
import getpass
import platform
import glob
import tomllib

#Disable all delays in pyautogui
pyautogui.MINIMUM_DURATION=0
pyautogui.MINIMUM_SLEEP=0
pyautogui.PAUSE=0

#Disable failsafe that kills the program if the mouse goes into the corner of the screen, as this can be a problem in fullscreen emulators
pyautogui.FAILSAFE=False

OP_PATH = __file__[:__file__.rfind(os.sep)]
CONFIG_PATH = "DS_FPS_mousefix.toml"
with open(CONFIG_PATH, "rb") as f:
    CONFIG = tomllib.load(f)

MOUSEFIX_PATH = OP_PATH + os.sep + "mousefixes" + os.sep #Path of mousefixes

def distance(vec1, vec2):
    """Find pythagorean distance between two iterable vectors"""
    if len(vec1) != len(vec2):
        raise ValueError("Vectors cannot have different number of axes")
    return sum([x ** 2 for x in [vec2[i] - vec1[i] for i in range(len(vec1))]]) ** 0.5

class MousefixBase(threading.Thread):
    config = "default"

    def __init__(self, use_hud_detect = True, host_gui = None):
        """Nintendo DS Mousefix base"""
        super().__init__()
        self.use_hud_detect = use_hud_detect #Use HUD detection for auto-pausing and such
        self.host_gui = host_gui #Host GUI

    def __getitem__(self, key):
        """Get config for this mousefix, or reset to default"""
        try:
            return CONFIG["mousefix"][type(self).config][key]
        except KeyError: #Either we did not define the key or this mousefix has no config
            return CONFIG["mousefix"]["default"][key]

    @property
    def touch_center(self):
        """Relative center of touch area"""
        return self["scale"][0]//2, self["scale"][1]//2

    @property
    def mouse_drag_area_center(self):
        """Relative center of draggable area"""
        return sum(self["mouseDragAreaX"])//2, sum(self["mouseDragAreaY"])//2

    def get_touch_area(self):
        """Get the initial touch area and return touch_offset and touch_size"""
        print("Click opposite corners of the touch area.")
        mouse.wait(target_types=("down"))
        p1=mouse.get_position()
        print(p1)
        mouse.wait(target_types=("down"))
        p2=mouse.get_position()
        print(p2)
        touch_offset = min((p1[0], p2[0])), min((p1[1], p2[1]))
        touch_size = max((p1[0], p2[0])) - touch_offset[0], max((p1[1], p2[1])) - touch_offset[1]
        print("touch offset", touch_offset, "\ntouch size", touch_size)
        return touch_offset, touch_size

    def get_is_hud(self):
        """Detect if we are in the HUD, for auto pause"""
        return True

    def manual_pause_handler(self):
        """Handle manual pauses"""
        if self.manual_paused:
            while not self.keyevents.empty():
                e = self.keyevents.get()
                if e.event_type == "down" and e.name == CONFIG["pauseKey"]:
                    self.manual_paused = not self.manual_paused

            self.clear_queue(self.mouseevents) #Clear mouse events queue while waiting to unpause

            if not self.manual_paused: #We were unpaused in this check
                self.reset_mouse()
                print("Resumed.")
            else: #We are still paused, so wait and continue
                time.sleep(CONFIG["pauseInterval"])

        return self.manual_paused

    def run(self):
        """Start the program"""
        self.running = True
        self.touch_offset, self.touch_size = self.get_touch_area()
        keyboard.add_hotkey(CONFIG["killKey"], self.kill) #Kill the program when this key is pressed, no matter what

        self.keyevents=keyboard.start_recording()[0] #Get a keyboard events queue

        self.mouseevents=queue.Queue()
        mouse.hook(self.mouseevents.put_nowait) #Get a mouse events queue

        self.reset_mouse()

        self.last_hudcheck = 0 #Time of last HUD check
        self.was_hud = True #Was HUD last time we checked
        self.is_hud = True #Is hud on this check
        self.manual_paused = False

        while self.running:
            if self.manual_pause_handler(): #Handle any possible unpauses, delay if not unpaused
                continue

            #If auto pause is enabled and it has been more than CONFIG["hudCheckInterval"] seconds since we last checked for the HUD...
            if self.use_hud_detect and time.time()-self.last_hudcheck>CONFIG["hudCheckInterval"]:
                self.last_hudcheck=time.time()
                self.is_hud = self.get_is_hud()
                if not self.was_hud and self.is_hud:
                    print("Hud detected. Engaging...")
                    self.reset_mouse()
                elif not self.is_hud and self.was_hud:
                    print("Hud disappeared. Pausing...")
                    pyautogui.mouseUp()
                self.was_hud = self.is_hud
                if not self.is_hud:
                    time.sleep(CONFIG["hudCheckInterval"])

                    #Clear mouse and keyboard events while paused
                    for q in (self.keyevents, self.mouseevents):
                        self.clear_queue(q)

                    continue


            if not self.keyevents.empty(): #Do not hold the loop waiting for a keyboard event
                e = self.keyevents.get()
                if e.event_type != "down": #Only kare about key down events
                    continue
                if e.name in self["keybinds"].keys(): #Deals with keys in the key bindings configuration
                    print(self["keybinds"][e.name])

                    try:
                        self.touchbutton(self["touchButtons"][self["keybinds"][e.name]]) #Push the button associated with the keybinding
                        #Todo: Maybe convert this to lambdas?
                    except KeyError: #Not a regular touchbutton, so call our special method for that keybind
                        exec("self."+self["keybinds"][e.name].lower()+"(e)")

                elif e.name.isnumeric() and 0 < int(e.name) <= len(self["weaponSelectButtons"]): #Pressed a number key, is in range of weapons
                    print("Weapon %i selected" % int(e.name))
                    self.weaponselect(int(e.name))

                elif e.name == CONFIG["pauseKey"]: #Pause the mouse fix
                    print("Paused")
                    pyautogui.mouseUp()
                    self.manual_paused = True
                    continue

            if not self.mouseevents.empty(): #Do not hold the loop waiting for a mouse event
                e = self.mouseevents.get()
                if type(e)==mouse.ButtonEvent and e.button in CONFIG["mousebinds"].keys():
                    exec("self."+CONFIG["mousebinds"][e.button]+"(e)") #Run one of our three mouse bound functions

            if not mouse.is_pressed(): #Give up wrap if mouse is actually held down
                self.mousewrap(*self.abs_to_rel(*mouse.get_position())) #Perform a mouse wrap enforcement check

    def clear_queue(self, q):
        """Clears the passed queue"""
        while not q.empty():
            q.get()

    def kill(self, destroy_gui = True):
        """Exit the mousefix."""
        self.running=False
        try:
            pyautogui.mouseUp()
            keyboard.stop_recording()
        finally:
            if self.host_gui and destroy_gui: #We were passed a host GUI at startup, and told in this call to destroy it
                self.host_gui.destroy() #Kill the host GUI when the mousefix exits
            quit()

    def weaponselect(self, weapon):
        """Select a weapon by index"""
        pass

    def fire(self, e):
        """Fire the gun, or stop firing"""
        if e.event_type=="down":
            pyautogui.keyDown(CONFIG["emuKeys"]["shoulder"]["L"])
        else:
            pyautogui.keyUp(CONFIG["emuKeys"]["shoulder"]["L"])
            if self.out_of_drag_bounds(*self.abs_to_rel(*mouse.get_position())) != (0, 0): #Mouse moved out of bounds while holding a charged shot
                self.reset_mouse()
            else:
                pyautogui.mouseDown() #The mouse has been truly released, so simulate pressing it again

    def zoom_out(self, e):
        """Press or release the zoom out key"""
        #print("CONFIG["emuKeys"]["shoulder"]["R"] "+e.event_type)
        if e.event_type == "down":
            pyautogui.keyDown(CONFIG["emuKeys"]["shoulder"]["R"])
        else:
            pyautogui.keyUp(CONFIG["emuKeys"]["shoulder"]["R"])

    def out_of_drag_bounds(self, x, y):
        """Check if coordinates are out of dragging bounds, and return x, y tuple of sign of CONFIG["directions"]"""
        return - (x < self["mouseDragAreaX"][0] + CONFIG["mouseDragMargin"]) + (x > self["mouseDragAreaX"][1] - CONFIG["mouseDragMargin"]), - (y < self["mouseDragAreaY"][0] + CONFIG["mouseDragMargin"]) + (y > self["mouseDragAreaY"][1] - CONFIG["mouseDragMargin"])

    def mousewrap(self, x, y):
        """Check if the mouse needs wrapping and perform if needed"""
        oob = self.out_of_drag_bounds(x, y)
        if oob == (0, 0):
            return

        print("Wrapping mouse")
        pyautogui.mouseUp()
        time.sleep(CONFIG["mouseResetWait"])
        self.goto_relative(
             (self["mouseDragAreaX"][1], self.mouse_drag_area_center[0], self["mouseDragAreaX"][0])[oob[0] + 1] + CONFIG["mouseDropMargin"] * oob[0],
             (self["mouseDragAreaY"][1], self.mouse_drag_area_center[1], self["mouseDragAreaY"][0])[oob[1] + 1] + CONFIG["mouseDropMargin"] * oob[1])
        pyautogui.mouseDown()

    def rel_to_abs(self, x, y):
        """Convert relative touch position to real screen position"""
        return int(self.touch_offset[0]+x/self["scale"][0]*self.touch_size[0]), int(self.touch_offset[1]+y/self["scale"][1]*self.touch_size[1])

    def abs_to_rel(self, x, y):
        """Convert real screen position to relative touch position"""
        return int((x-self.touch_offset[0])/self.touch_size[0]*self["scale"][0]+0.5), int((y-self.touch_offset[1])/self.touch_size[1]*self["scale"][1]+0.5)

    def goto_relative(self, x, y):
        """Move the mouse cursor to a relative touch position"""
        #mouse.move(*self.rel_to_abs(x, y))
        pyautogui.moveTo(*self.rel_to_abs(x, y))

    def touchbutton(self, button, reset = True):
        """Push a touch button in form ((x, y), wait). If not wait, default is used. If not reset, keep holding"""
        pyautogui.mouseUp()
        time.sleep(CONFIG["mouseResetWait"])
        self.goto_relative(*button[0])
        pyautogui.mouseDown()

        if button[1]: #If the specific button wait is false or zero, use the default button wait
            button_wait = button[1]
        else:
            button_wait = CONFIG["buttonWait"]

        for i in range(int(button_wait / CONFIG["buttonHoldInterval"])): #Lock the mouse onto the button by constantly moving back to it
            time.sleep(CONFIG["buttonHoldInterval"])
            self.goto_relative(*button[0])
        time.sleep(button_wait % CONFIG["buttonHoldInterval"])

        if reset:
            self.reset_mouse()

    def reset_mouse(self, e=None):
        """Reset the mouse to the center position"""
        pyautogui.mouseUp()
        time.sleep(CONFIG["mouseResetWait"])
        self.goto_relative(*self.mouse_drag_area_center)
        pyautogui.mouseDown()

#Load and register the mousefixes
mousefix_registry = {}
for script_fn in glob.glob(MOUSEFIX_PATH + "*"):
    script = open(script_fn)
    exec(script.read())
    mousefix_registry[name] = mousefix #Each mousefix must end with a name variable set to a pretty name string, and a mousefix variable set to the new mousefix class

class MousefixWindow(tk.Tk):
    def __init__(self):
        """Window to choose and start a mousefix"""
        super().__init__()
        self.title("DS FPS Mouse Fixer")
        self.START_DELAY = 3 #Delay after pressing start to actually start
        self.INFO_STRING = "Select a game from the menu, then press Start. You will have %i seconds to switch to the emulator window, before this window turns red, indicating the mousefix is active. Once it turns red, click two diagonal opposite corners of the stylus play area.\nREMINDER: %s pauses the mouse fix, %s kills it. Enjoy!\nS.D.G." % (self.START_DELAY, CONFIG["pauseKey"], CONFIG["killKey"])

        self.mousefix=None
        self.build()
        self.mainloop()

        #Called after window is closed
        if self.mousefix: #A mousefix was running
            self.mousefix.kill(destroy_gui = False)
            self.mousefix.join()

    def build(self):
        """Construct the GUI"""
        self.geometry("400x300")

        #Using a frame to get rid of all widgets after a mousefix has been started
        self.mainframe = tk.Frame(self)
        self.mainframe.grid(sticky = tk.NSEW)
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        #Choose a mousefix
        self.mousefix_choice = tk.StringVar(self)
        self.mousefix_chooser = tk.OptionMenu(self.mainframe, self.mousefix_choice, *mousefix_registry.keys())
        self.mousefix_chooser.grid(row = 0, sticky = tk.E + tk.W)

        #Choose wether to enable HUD detection for auto-pause and other features
        self.hud_detect_choice = tk.BooleanVar(self, value = True)
        self.hud_detect_chooser = tk.Checkbutton(self.mainframe, text = "Use HUD detection features", variable = self.hud_detect_choice)
        self.hud_detect_chooser.grid(row = 1, sticky = tk.E + tk.W)

        #Start button
        self.start_button = tk.Button(self.mainframe, text = "Start", command = self.launch_mousefix)
        self.start_button.grid(row = 2, sticky = tk.E + tk.W)

        #Additional help information display
        self.info_text = tk.Text(self.mainframe, wrap = "word")
        self.info_text.grid(row = 3, sticky = tk.NSEW)
        self.info_text.insert(0.0, self.INFO_STRING)
        self.info_text.configure(state = "disabled")
        self.mainframe.rowconfigure(3, weight = 1)

        self.mainframe.columnconfigure(0, weight = 1)


    def launch_mousefix(self):
        """Launch a mousefix"""
        if not self.mousefix_choice.get(): #No mousefix was chosen
            mb.showerror("No mousefix selected", "You must first select a mousefix from the option menu.")
            return

        if getpass.getuser() != "root" and platform.system() == "Linux": #Must run script as root on Linux
            mb.showerror(title = "Root priviledges required", message = "Directly reading device events on Linux requires root priviledges. Try running this script again using the `sudo` command.")
            self.destroy()
            quit()
            return

        #Startup the mousefix
        self.mousefix = mousefix_registry[self.mousefix_choice.get()](use_hud_detect = self.hud_detect_choice.get(), host_gui = self)
        self.mainframe.destroy() #Get rid of all widgets
        time.sleep(self.START_DELAY) #Should probably be threaded, tbh
        self.mousefix.start()
        self.configure(bg = "red")

MousefixWindow()
