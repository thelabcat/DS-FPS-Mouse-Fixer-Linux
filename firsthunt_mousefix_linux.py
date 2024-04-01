#!/usr/bin/env python3
#Adaptation of the MPH mousefix for Linux, for MPH: First Hunt, ver 1.0
#S.D.G.

"""
NOTES:
- Boost ball should not be handled by the mousefix, as it works via a double-tap of direction buttons.
"""

import MPH_mousefix_linux as mph
import mouse
import keyboard
import pyautogui #For HUD detection and working around faults in the mouse and keyboard modules
import time
import queue

mph.SCALE = (1280, 960) #Size of reference window
mph.TOUCH_CENTER = mph.SCALE[0]//2, mph.SCALE[1]//2

#Limits of where to wrap the mouse
mph.MOUSE_DRAG_AREA_X = (0, 1115)
mph.MOUSE_DRAG_AREA_Y = (0, 555)
mph.MOUSE_DRAG_AREA_CENTER = sum(mph.MOUSE_DRAG_AREA_X)//2, sum(mph.MOUSE_DRAG_AREA_Y)//2 #Center of draggable area

mph.IS_HUD_COORDS = (45, 625) #Coordinates to check for color match if we are in HUD or elsewhere
mph.VARIA_ORANGE = 219, 162, 56 #Color of varia components in HUD

mph.KEYBINDS = {'q': 'MAIN_WEAPON',
            'e': 'MISSILES',
            'r': 'THIRD_WEAPON',
##            'f': 'SCAN_VISOR',
##            'z': 'PAGE_LEFT',
##            'c': 'PAGE_RIGHT',
##            'x': 'OK',
##            'v': 'YES',
##            'b': 'NO',
            'ctrl': 'MORPH_BALL',
##            'tab': 'BOOST_BALL'
            'space': 'JUMP'
            }

mph.TOUCHBUTTONS = { #Each button's position, and how long to press it
    "MAIN_WEAPON" : ((930, 864), mph.BUTTON_WAIT),
    "MISSILES" : ((1090, 744), mph.BUTTON_WAIT),
    "THIRD_WEAPON" : ((1200, 579), mph.BUTTON_WAIT),
##    "SCAN_VISOR" : ((450, 608), 0.5),
##    "PAGE_LEFT" : ((250, 495), BUTTON_WAIT),
##    "PAGE_RIGHT" : ((650, 495), BUTTON_WAIT),
##    "OK" : ((450, 495), BUTTON_WAIT),
##    "YES" : ((337, 495), BUTTON_WAIT),
##    "NO" : ((563, 495), BUTTON_WAIT),
    "MORPH_BALL" : ((165, 780), mph.BUTTON_WAIT),
##    "WEAPON_SELECT" : ((810, 120), BUTTON_WAIT)
    }

mph.WEAPONSELECT_BUTTONS = ( #Buttons of the three weapons for numerical selection
    mph.TOUCHBUTTONS["MAIN_WEAPON"],
    mph.TOUCHBUTTONS["MISSILES"],
    mph.TOUCHBUTTONS["THIRD_WEAPON"],
    )
    
class FirstHuntMousefix(mph.MPHMousefix):
    
    def __init__(self, run=True, use_hud_check=True):
        """MouseFix for Metroid Prime: Hunters [First Hunt]"""
        self.use_hud_check = use_hud_check
        
        self.touch_offset, self.touch_size = self.get_touch_area()
        if run: #Do not start the mouse fix unless run is True
            self.mainloop()

    def get_is_morphball(self):
        """Are we in morphball mode, not standing? Assumes we are in the Varia HUD"""
        raise NotImplemented("No current way to detect morphball.")
    
    def mainloop(self):
        """Start the program"""
        self.running=True
        keyboard.add_hotkey(mph.KILL_KEY, self.kill) #Kill the program when this key is pressed, no matter what
        
        keyevents=keyboard.start_recording()[0] #Get a keyboard events queue
        
        mouseevents=queue.Queue()
        mouse.hook(mouseevents.put_nowait) #Get a mouse events queue
        
        self.reset_mouse()
        
        last_hudcheck=0 #Time of last HUD check
        was_hud=True
        is_hud=True
        is_paused=False

        while self.running:
            if is_paused:
                while not keyevents.empty():
                    e = keyevents.get()
                    if e.event_type == "down" and e.name == mph.PAUSE_KEY:
                        is_paused = not is_paused
                            
                self.clear_queue(mouseevents) #Clear mouse events queue while waiting to unpause
                    
                if not is_paused: #We were unpaused in this check
                    self.reset_mouse()
                    print("Resumed.")
                else: #We are still paused, so wait and continue
                    time.sleep(mph.PAUSE_INTERVAL)
                    continue

            #If we are set to use the HUD check auto-pause and it has been more than HUD_CHECK_INTERVAL seconds since we last checked for Samus's HUD...
            if self.use_hud_check and time.time()-last_hudcheck>mph.HUD_CHECK_INTERVAL:
                last_hudcheck=time.time()
                is_hud=self.get_is_hud()
                if not was_hud and is_hud:
                    print("Hud detected. Engaging...")
                    self.reset_mouse()
                elif not is_hud and was_hud:
                    print("Hud disappeared. Pausing...")
                    pyautogui.mouseUp()
                was_hud=is_hud
                if not is_hud:
                    time.sleep(mph.HUD_CHECK_INTERVAL)

                    #Clear mouse and keyboard events while paused
                    for q in (keyevents, mouseevents):
                        self.clear_queue(q)
                    
                    continue
                
            if not keyevents.empty(): #Do not hold the loop waiting for a keyboard event
                e = keyevents.get()
                if e.event_type != "down": #Only care about key down events
                    continue
                if e.name in mph.KEYBINDS.keys(): #Deals with keys in the key bindings configuration
                    print(mph.KEYBINDS[e.name])
                    try:
                        self.touchbutton(mph.TOUCHBUTTONS[mph.KEYBINDS[e.name]]) #Push the button associated with the keybinding
                    except KeyError: #Not a regular touchbutton
                        exec("self."+mph.KEYBINDS[e.name].lower()+"(e)")
                    
                elif e.name.isnumeric() and 0 < int(e.name) <= len(mph.WEAPONSELECT_BUTTONS): #Pressed a number key, is in range of weapons
                    print("Weapon %i selected" % int(e.name))
                    self.weaponselect(int(e.name))
                    
                elif e.name == mph.PAUSE_KEY: #Pause the mouse fix
                    print("Paused")
                    pyautogui.mouseUp()
                    is_paused=True
                    continue
                        
            if not mouseevents.empty(): #Do not hold the loop waiting for a mouse event
                e = mouseevents.get()
                if type(e)==mouse.ButtonEvent and e.button in mph.MOUSEBINDS.keys():
                    exec("self."+mph.MOUSEBINDS[e.button]+"(e)") #Run one of our three mouse bound functions

            if not mouse.is_pressed(): #Give up wrap if mouse is actually held down
                self.mousewrap(*self.abs_to_rel(*mouse.get_position())) #Perform a mouse wrap enforcement check

    def clear_queue(self, q):
        """Clears the passed queue"""
        while not q.empty():
            q.get()
            
    def kill(self):
        """End the program."""
        self.running=False
        try:
            pyautogui.mouseUp()
            keyboard.stop_recording()
        finally:
            quit()
    
    def weaponselect(self, weapon):
        """Select a weapon by index 1-3"""
        self.touchbutton(mph.WEAPONSELECT_BUTTONS[weapon-1])

    def zoom_out(self, e):
        """Press or release the zoom out key"""
        #print("ZOOMOUT_KEY "+e.event_type)
        if e.event_type == "down":
            pyautogui.keyDown(mph.ZOOMOUT_KEY)
        elif e.event_type == "up":
            pyautogui.keyUp(mph.ZOOMOUT_KEY)

    def jump(self, e):
        """Perform a double-tap jump"""
        if e.event_type == "down":
            for i in range(2):
                self.reset_mouse()
                time.sleep(mph.BUTTON_WAIT)

if __name__ == "__main__":
    mmf=FirstHuntMousefix(use_hud_check = not "n" in input("Use HUD check auto-pause? [Y]/n: ").lower())
