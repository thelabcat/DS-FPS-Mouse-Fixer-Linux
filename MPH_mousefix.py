#!/usr/bin/env python3
#MPH mouse fix for Linux, ver 2.0
#S.D.G.

from DS_FPS_mousefix_linux import *

class MPHMousefix(MousefixBase):
    def __init__(self, MULTIPLAYER = True):
        super(type(self), self).__init__(USE_AUTO_PAUSE = not MULTIPLAYER)
        self.MULTIPLAYER = MULTIPLAYER

        self.SCALE = (900, 674) #Size of reference window

        #Limits of where to wrap the mouse
        self.MOUSE_DRAG_AREA_X = (0,  self.SCALE[0])
        self.MOUSE_DRAG_AREA_Y = (225, 495)

        self.BOOST_SWIPE_SIZE = 400 #The pixel length a boost swipe must be for the ROM to recognize it

        self.IS_HUD_COORDS = (MOUSE_DRAG_MARGIN,  self.SCALE[1] - MOUSE_DRAG_MARGIN) #Coordinates to check for color match if we are in HUD or in the ship
        self.IS_MORPHBALL_COORDS = (800, 530) #Coordinates to check if we are in morphball mode or not
        self.VARIA_ORANGE = 211, 154, 73 #Color of varia components in HUD
        self.COLOR_TOLERANCE = 10

        self.DEFAULT_BB_DIRECTION = "UP" #Default direction to touch-based boost ball in

        #Most key bindings
        self.KEYBINDS = {'q': 'MAIN_WEAPON',
                    'e': 'MISSILES',
                    'r': 'THIRD_WEAPON',
                    'f': 'SCAN_VISOR',
                    'z': 'PAGE_LEFT',
                    'c': 'PAGE_RIGHT',
                    'x': 'OK',
                    'v': 'YES',
                    'b': 'NO',
                    'ctrl': 'MORPH_BALL',
                    'tab': 'BOOST_BALL'
                    }

        self.TOUCHBUTTONS = { #Each button's position, and how long to press it
            "MAIN_WEAPON" : ((300, 112), BUTTON_WAIT),
            "MISSILES" : ((440, 113), BUTTON_WAIT),
            "THIRD_WEAPON" : ((605, 120), BUTTON_WAIT),
            "SCAN_VISOR" : ((450, 608), 0.5),
            "PAGE_LEFT" : ((250, 495), BUTTON_WAIT),
            "PAGE_RIGHT" : ((650, 495), BUTTON_WAIT),
            "OK" : ((450, 495), BUTTON_WAIT),
            "YES" : ((337, 495), BUTTON_WAIT),
            "NO" : ((563, 495), BUTTON_WAIT),
        #    "PAGE_LEFT" : ((288, 515), BUTTON_WAIT),
        #    "PAGE_RIGHT" : ((612, 515), BUTTON_WAIT),
            "MORPH_BALL" : ((775, 585), BUTTON_WAIT),
            "WEAPON_SELECT" : ((810, 120), BUTTON_WAIT)
            }

        self.WEAPONSELECT_BUTTONS = ( #Positions of each weapon in the weapon select pie menu
            (327, 168),
            (341, 302),
            (373, 439),
            (485, 555),
            (622, 590),
            (763, 604),
            )

    def get_is_hud(self):
        """Are we in the Varia HUD, not in the ship? Does not work in weapon select"""
        return pyautogui.pixelMatchesColor(*self.rel_to_abs(*self.IS_HUD_COORDS), self.VARIA_ORANGE, self.COLOR_TOLERANCE)

    def get_is_morphball(self):
        """Are we in morphball mode, not standing? Assumes we are in the Varia HUD"""
        return pyautogui.pixelMatchesColor(*self.rel_to_abs(*self.IS_MORPHBALL_COORDS), self.VARIA_ORANGE, self.COLOR_TOLERANCE)

    def weaponselect(self, weapon):
        """Select a weapon by index 1-6"""
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        self.goto_relative(*self.TOUCHBUTTONS["WEAPON_SELECT"][0])
        pyautogui.mouseDown()
        time.sleep(self.TOUCHBUTTONS["WEAPON_SELECT"][1])
        self.goto_relative(*self.WEAPONSELECT_BUTTONS[weapon-1])
        time.sleep(BUTTON_WAIT)
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        self.reset_mouse()

    def zoom_out(self, e):
        """Press or release the zoom out key, sacrificing mouse drag for boost ball"""
        #print("R_SHOULDER_KEY "+e.event_type)
        if e.event_type == "down":
            pyautogui.keyDown(R_SHOULDER_KEY, )
        elif e.event_type == "up":
            pyautogui.keyUp(R_SHOULDER_KEY, )

        if not self.MULTIPLAYER and self.get_is_morphball(): #Sacrifice steering for via-button boost ball
            if e.event_type == "down":
                pyautogui.mouseUp()
            elif e.event_type == "up":
                self.reset_mouse()

    def boost_ball(self, e):
        """Perform a touch-based boost ball"""
        pyautogui.mouseUp()
        time.sleep(MOUSE_RESET_WAIT)
        
        direction=[0, 0]
        
        for key in DPAD_KEYS.keys(): #Sum input directions. If they contradict, they will zero out
            if keyboard.is_pressed(key):
                #print(key)
                direction[0]+=DIRECTIONS[DPAD_KEYS[key]][0]
                direction[1]+=DIRECTIONS[DPAD_KEYS[key]][1]
                
        if direction == [0, 0]: #If there is no direction or all input directions cancelled out, use the default
            direction = DIRECTIONS[self.DEFAULT_BB_DIRECTION]

        end_x = self.touch_center[0]+self.BOOST_SWIPE_SIZE//2*direction[0]
        end_y = self.touch_center[1]+self.BOOST_SWIPE_SIZE//2*direction[1]

        start_x = self.touch_center[0]-self.BOOST_SWIPE_SIZE/2*direction[0]
        start_y = self.touch_center[1]-self.BOOST_SWIPE_SIZE//2*direction[1]
        #print("Direction is", direction)
        #print("Boost from ", start_x, start_y, "to", end_x, end_y)
        self.goto_relative(start_x, start_y)
        time.sleep(MOUSE_RESET_WAIT)
        pyautogui.mouseDown()
        time.sleep(MOUSE_RESET_WAIT)
        self.goto_relative(end_x, end_y)
        time.sleep(MOUSE_RESET_WAIT)
        self.reset_mouse()

if __name__ == "__main__":
    mmf=MPHMousefix(MULTIPLAYER = "y" in input("Are you going into multiplayer? y/[N]: ").lower())
    mmf.start()
