#!/usr/bin/env python3
#Nintendo DS FPS mousefix for linux - base module
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

#Disable all delays in pyautogui
pyautogui.MINIMUM_DURATION=0
pyautogui.MINIMUM_SLEEP=0
pyautogui.PAUSE=0

#Disable failsafe that kills the program if the mouse goes into the corner of the screen, as this can be a problem in fullscreen emulators
pyautogui.FAILSAFE=False

MOUSE_RESET_WAIT = 35/1000 #pertains to the time before the mouse moves again, adjust this if your camera keeps jerking when your cursor is reset to center.
BUTTON_WAIT = 120/1000 #pertains to the time before the mouse moves after pressing a button, adjust this if you get ghost inputs (buttons not properly pressed).
KEY_WAIT = 50/1000 #pertains to the time between key inputs, this is used for some macros such as sprinting and crouching in the COD Games, adjust this if those inputs are not caught.
HUD_CHECK_INTERVAL = 1 #How often to check if Samus's HUD is shown
PAUSE_INTERVAL = 0.1 #How often to run the pause loop
BUTTON_HOLD_INTERVAL = 0.05 #How often to rerun the mouse movement command to keep the cursor locked onto a button

MOUSE_DRAG_MARGIN = 5 #How close we can get to the edge before we wrap
MOUSE_DROP_MARGIN = MOUSE_DRAG_MARGIN*2 #How far away from the other edge to drop the cursor when we wrap

#Keys that the DS emulator is set to interpret as D-pad
DPAD_KEYS = {"w":"UP",
             "s":"DOWN",
             "d":"RIGHT",
             "a":"LEFT"
             }

#Keys that the emulator is set to interpret as shoulder button presses
L_SHOULDER_KEY = "n" #Used for firing
R_SHOULDER_KEY = "m" #Used for zooming


PAUSE_KEY="\\" #Pause the mouse fix manually
KILL_KEY="backspace" #Kill the mouse fix

#Direction names as mapped to screen coordinate factors
DIRECTIONS = {"UP":(0, -1),
              "DOWN":(0, 1),
              "RIGHT":(1, 0),
              "LEFT":(-1, 0)
              }


MOUSEBINDS = { #Mouse bindings
    "left" : "fire",
    "middle" : "reset_mouse",
    "right" : "zoom_out"
    }

MOUSEFIX_PATH = __file__[:__file__.rfind(os.sep)] + os.sep + "mousefixes" + os.sep #Path of mousefixes

class MousefixBase(threading.Thread):
    def __init__(self, USE_HUD_DETECT = True, host_gui = None):
        """Nintendo DS Mousefix base"""
        super().__init__()
        self.USE_HUD_DETECT = USE_HUD_DETECT #Use HUD detection for auto-pausing and such
        self.host_gui = host_gui #Host GUI

        #Scale of touchscreen and size of drag area
        self.SCALE = (900, 674) #Size of reference window
        self.MOUSE_DRAG_AREA_X = (0, self.SCALE[0]) #Range of X coordinates we can drag in
        self.MOUSE_DRAG_AREA_Y = (0, self.SCALE[1]) #Range of Y coordinates we can drag in

        self.KEYBINDS = {} #Keybindings
        self.TOUCHBUTTONS = {} #Each button's position, and how long to press it
        self.WEAPONSELECT_BUTTONS = () #Weapon selection buttons by numerical index

    @property
    def touch_center(self):
        """Relative center of touch area"""
        return self.SCALE[0]//2, self.SCALE[1]//2

    @property
    def mouse_drag_area_center(self):
        """Relative center of draggable area"""
        return sum(self.MOUSE_DRAG_AREA_X)//2, sum(self.MOUSE_DRAG_AREA_Y)//2

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
        pass

    def manual_pause_handler(self):
        """Handle manual pauses"""
        if self.manual_paused:
            while not self.keyevents.empty():
                e = self.keyevents.get()
                if e.event_type == "down" and e.name == PAUSE_KEY:
                    self.manual_paused = not self.manual_paused

            self.clear_queue(self.mouseevents) #Clear mouse events queue while waiting to unpause

            if not self.manual_paused: #We were unpaused in this check
                self.reset_mouse()
                print("Resumed.")
            else: #We are still paused, so wait and continue
                time.sleep(PAUSE_INTERVAL)

        return self.manual_paused

    def run(self):
        """Start the program"""
        self.running=True
        self.touch_offset, self.touch_size = self.get_touch_area()
        keyboard.add_hotkey(KILL_KEY, self.kill) #Kill the program when this key is pressed, no matter what

        self.keyevents=keyboard.start_recording()[0] #Get a keyboard events queue

        self.mouseevents=queue.Queue()
        mouse.hook(self.mouseevents.put_nowait) #Get a mouse events queue

        self.reset_mouse()

        self.last_hudcheck=0 #Time of last HUD check
        self.was_hud=True #Was HUD last time we checked
        self.is_hud=True #Is hud on this check
        self.manual_paused=False

        while self.running:
            if self.manual_pause_handler(): #Handle any possible unpauses, delay if not unpaused
                continue

            #If auto pause is enabled and it has been more than HUD_CHECK_INTERVAL seconds since we last checked for the HUD...
            if self.USE_HUD_DETECT and time.time()-self.last_hudcheck>HUD_CHECK_INTERVAL:
                self.last_hudcheck=time.time()
                self.is_hud=self.get_is_hud()
                if not self.was_hud and self.is_hud:
                    print("Hud detected. Engaging...")
                    self.reset_mouse()
                elif not self.is_hud and self.was_hud:
                    print("Hud disappeared. Pausing...")
                    pyautogui.mouseUp()
                self.was_hud=self.is_hud
                if not self.is_hud:
                    time.sleep(HUD_CHECK_INTERVAL)

                    #Clear mouse and keyboard events while paused
                    for q in (self.keyevents, self.mouseevents):
                        self.clear_queue(q)

                    continue


            if not self.keyevents.empty(): #Do not hold the loop waiting for a keyboard event
                e = self.keyevents.get()
                if e.event_type != "down": #Only kare about key down events
                    continue
                if e.name in self.KEYBINDS.keys(): #Deals with keys in the key bindings configuration
                    print(self.KEYBINDS[e.name])

                    try:
                        self.touchbutton(self.TOUCHBUTTONS[self.KEYBINDS[e.name]]) #Push the button associated with the keybinding
                        #Todo: Maybe convert this to lambdas?
                    except KeyError: #Not a regular touchbutton, so call our special method for that keybind
                        exec("self."+self.KEYBINDS[e.name].lower()+"(e)")

                elif e.name.isnumeric() and 0 < int(e.name) <= len(self.WEAPONSELECT_BUTTONS): #Pressed a number key, is in range of weapons
                    print("Weapon %i selected" % int(e.name))
                    self.weaponselect(int(e.name))

                elif e.name == PAUSE_KEY: #Pause the mouse fix
                    print("Paused")
                    pyautogui.mouseUp()
                    self.manual_paused = True
                    continue

            if not self.mouseevents.empty(): #Do not hold the loop waiting for a mouse event
                e = self.mouseevents.get()
                if type(e)==mouse.ButtonEvent and e.button in MOUSEBINDS.keys():
                    exec("self."+MOUSEBINDS[e.button]+"(e)") #Run one of our three mouse bound functions

            if not mouse.is_pressed(): #Give up wrap if mouse is actually held down
                self.mousewrap(*self.abs_to_rel(*mouse.get_position())) #Perform a mouse wrap enforcement check

    def clear_queue(self, q):
        """Clears the passed queue"""
        while not q.empty():
            q.get()

    def kill(self):
        """Exit the mousefix."""
        self.running=False
        try:
            pyautogui.mouseUp()
            keyboard.stop_recording()
        finally:
            if self.host_gui: #We were passed a host GUI
                self.host_gui.destroy() #Kill the host GUI when the mousefix exits
            quit()

    def weaponselect(self, weapon):
        """Select a weapon by index"""
        pass

    def fire(self, e):
        """Fire the gun, or stop firing"""
        if e.event_type=="down":
            pyautogui.keyDown(L_SHOULDER_KEY)
        else:
            pyautogui.keyUp(L_SHOULDER_KEY)
            if self.out_of_drag_bounds(*self.abs_to_rel(*mouse.get_position())) != (0, 0): #Mouse moved out of bounds while holding a charged shot
                self.reset_mouse()
            else:
                pyautogui.mouseDown() #The mouse has been truly released, so simulate pressing it again

    def zoom_out(self, e):
        """Press or release the zoom out key"""
        #print("R_SHOULDER_KEY "+e.event_type)
        if e.event_type == "down":
            pyautogui.keyDown(R_SHOULDER_KEY)
        else:
            pyautogui.keyUp(R_SHOULDER_KEY)

    def out_of_drag_bounds(self, x, y):
        """Check if coordinates are out of dragging bounds, and return x, y tuple of sign of directions"""
        return - (x < self.MOUSE_DRAG_AREA_X[0] + MOUSE_DRAG_MARGIN) + (x > self.MOUSE_DRAG_AREA_X[1] - MOUSE_DRAG_MARGIN), - (y < self.MOUSE_DRAG_AREA_Y[0] + MOUSE_DRAG_MARGIN) + (y > self.MOUSE_DRAG_AREA_Y[1] - MOUSE_DRAG_MARGIN)

    def mousewrap(self, x, y):
        """Check if the mouse needs wrapping and perform if needed"""
        oob = self.out_of_drag_bounds(x, y)
        if oob == (0, 0):
            return

        print("Wrapping mouse")
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        self.goto_relative(
             (self.MOUSE_DRAG_AREA_X[1], self.mouse_drag_area_center[0], self.MOUSE_DRAG_AREA_X[0])[oob[0] + 1] + MOUSE_DROP_MARGIN * oob[0],
             (self.MOUSE_DRAG_AREA_Y[1], self.mouse_drag_area_center[1], self.MOUSE_DRAG_AREA_Y[0])[oob[1] + 1] + MOUSE_DROP_MARGIN * oob[1])
        pyautogui.mouseDown()

    def rel_to_abs(self, x, y):
        """Convert relative touch position to real screen position"""
        return int(self.touch_offset[0]+x/self.SCALE[0]*self.touch_size[0]), int(self.touch_offset[1]+y/self.SCALE[1]*self.touch_size[1])

    def abs_to_rel(self, x, y):
        """Convert real screen position to relative touch position"""
        return int((x-self.touch_offset[0])/self.touch_size[0]*self.SCALE[0]+0.5), int((y-self.touch_offset[1])/self.touch_size[1]*self.SCALE[1]+0.5)

    def goto_relative(self, x, y):
        """Move the mouse cursor to a relative touch position"""
        #mouse.move(*self.rel_to_abs(x, y))
        pyautogui.moveTo(*self.rel_to_abs(x, y))

    def touchbutton(self, button):
        """Push a touch button in form ((x, y), wait)"""
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        self.goto_relative(*button[0])
        pyautogui.mouseDown()

        for i in range(int(button[1] / BUTTON_HOLD_INTERVAL)): #Lock the mouse onto the button by constantly moving back to it
            time.sleep(BUTTON_HOLD_INTERVAL)
            self.goto_relative(*button[0])
        time.sleep(button[1] % BUTTON_HOLD_INTERVAL)

        self.reset_mouse()

    def reset_mouse(self, e=None):
        """Reset the mouse to the center position"""
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        self.goto_relative(*self.mouse_drag_area_center)
        pyautogui.mouseDown()

#Load and register the mousefixes
mousefix_registry = {}
for script_fn in glob.glob(MOUSEFIX_PATH + "*"):
    script = open(script_fn)
    exec(script.read())
    mousefix_registry[name] = mousefix

class MousefixWindow(tk.Tk):
    def __init__(self):
        """Window to choose and start a mousefix"""
        super().__init__()
        self.title("DS FPS Mouse Fixer")
        self.START_DELAY = 3 #Delay after pressing start to actually start
        self.INFO_STRING = "Select a game from the menu, then press Start. You will have %i seconds to switch to the emulator window, before this window turns red, indicating the mousefix is active. Once it turns red, click two diagonal opposite corners of the stylus play area.\nREMINDER: %s pauses the mouse fix, %s kills it. Enjoy!\nS.D.G." % (self.START_DELAY, PAUSE_KEY, KILL_KEY)

        self.mousefix=None
        self.build()
        self.mainloop()

        #Called after window is closed
        self.mousefix.kill()
        self.mousefix.join()

    def build(self):
        """Construct the GUI"""
        self.geometry("400x300")

        self.mainframe = tk.Frame(self)
        self.mainframe.grid(sticky = tk.NSEW)
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        self.mousefix_choice = tk.StringVar(self)
        self.mousefix_chooser = tk.OptionMenu(self.mainframe, self.mousefix_choice, *mousefix_registry.keys())
        self.mousefix_chooser.grid(row = 0, sticky = tk.E + tk.W)

        self.hud_detect_choice = tk.BooleanVar(self, value = True)
        self.hud_detect_chooser = tk.Checkbutton(self.mainframe, text = "Use HUD detection feature.", variable = self.hud_detect_choice)
        self.hud_detect_chooser.grid(row = 1, sticky = tk.E + tk.W)

        self.start_button = tk.Button(self.mainframe, text = "Start", command = self.launch_mousefix)
        self.start_button.grid(row = 2, sticky = tk.E + tk.W)

        self.info_text = tk.Text(self.mainframe, wrap = "word")
        self.info_text.grid(row = 3, sticky = tk.NSEW)
        self.info_text.insert(0.0, self.INFO_STRING)
        self.info_text.configure(state = "disabled")
        self.mainframe.rowconfigure(3, weight = 1)

        self.mainframe.columnconfigure(0, weight = 1)


    def launch_mousefix(self):
        """Launch a mousefix"""
        if not self.mousefix_choice.get(): #No mousefix was chosen
            return

        if getpass.getuser() != "root" and platform.system() == "Linux": #Must run script as root on Linux
            mb.showerror(title = "Root priviledges required", message = "Directly reading device events on Linux requires root priviledges. Try running this script again using the `sudo` command.")
            self.destroy()
            quit()
            return

        #Startup the mousefix
        self.mousefix = mousefix_registry[self.mousefix_choice.get()](USE_HUD_DETECT = self.hud_detect_choice.get(), host_gui = self) #Initialize the mousefix class we just loaded in
        self.mainframe.destroy()
        ## self.configure(bg = "green")
        time.sleep(self.START_DELAY)
        self.mousefix.start()
        self.configure(bg = "red")

MousefixWindow()
