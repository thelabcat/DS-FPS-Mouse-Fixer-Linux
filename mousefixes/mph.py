#!/usr/bin/env python3
#MPH mouse fix for Linux
#S.D.G.

class MPHMousefix(MousefixBase):
    config = "MPH"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hunter = "Samus" #Currently played hunter

    def get_is_hud(self):
        """Are we in the HUD, not in the ship? Does not work in weapon select. Also sets self.hunter"""
        screenshot = pyautogui.screenshot()

        hunter_detected = None #Which hunter did we detect first
        for h in self["hunterSpecs"].keys():
            if distance(screenshot.getpixel(self.rel_to_abs(*self["hunterSpecs"][h]["isHudCoords"])), self["hunterSpecs"][h]["isHudColor"]) < self["colorTolerance"]: #The color at the specified point is close to the right color.
                hunter_detected = h
                break

        if hunter_detected and hunter_detected != self.hunter: #If we detected a hunter and it's a new one
            print("New hunter detected: " + hunter_detected)
            self.hunter = hunter_detected

        return bool(hunter_detected) #Was there any hunter's HUD detected

    def get_is_altform(self):
        """Are we in alt form, not standing? Assumes we are in the Varia HUD. Depends on self.hunter being correct"""
        try:
            return pyautogui.pixelMatchesColor(*self.rel_to_abs(*self["hunterSpecs"][self.hunter]["isAltCoords"]), self["hunterSpecs"][self.hunter]["isAltColor"], self["colorTolerance"])
        except KeyError: #No isAltColor, so check for isNotAltColor instead
            return not pyautogui.pixelMatchesColor(*self.rel_to_abs(*self["hunterSpecs"][self.hunter]["isAltCoords"]), self["hunterSpecs"][self.hunter]["isNotAltColor"], self["colorTolerance"])

    def weaponselect(self, weapon):
        """Select a weapon by index 1-6"""
        self.touchbutton(self["touchButtons"]["weaponSelect"], reset = False)
        self.goto_relative(*self["weaponSelectButtons"][weapon-1])
        time.sleep(CONFIG["buttonWait"])
        pyautogui.mouseUp()
        time.sleep(CONFIG["mouseResetWait"])
        self.reset_mouse()

    def zoom_out(self, e):
        """Press or release the zoom out key, sacrificing mouse drag for boost ball"""
        #print("CONFIG["emuKeys"]["shoulder"]["R"] "+e.event_type)
        if e.event_type == "down":
            pyautogui.keyDown(CONFIG["emuKeys"]["shoulder"]["R"], )
        elif e.event_type == "up":
            pyautogui.keyUp(CONFIG["emuKeys"]["shoulder"]["R"], )

        if self.use_hud_detect and self.get_is_altform(): #Sacrifice steering for via-button boost ball
            if e.event_type == "down":
                print("Alt form detected, sacrificing steering.")
                pyautogui.mouseUp()
            elif e.event_type == "up":
                print("Steering restored")
                self.reset_mouse()

    def boost_ball(self, e):
        """Perform a touch-based boost ball"""
        pyautogui.mouseUp()
        time.sleep(CONFIG["mouseResetWait"])
        
        direction=[0, 0]
        
        for d in CONFIG["emuKeys"]["dPad"].keys(): #Sum input CONFIG["directions"]. If they contradict, they will zero out
            if keyboard.is_pressed(CONFIG["emuKeys"]["dPad"][d]):
                #print(key)
                direction[0]+=CONFIG["directions"][d][0]
                direction[1]+=CONFIG["directions"][d][1]
                
        if direction == [0, 0]: #If there is no direction or all input CONFIG["directions"] cancelled out, use the default
            direction = CONFIG["directions"][self["defaultBBDirection"]]

        end_x = self.touch_center[0]+self["boostSwipeSize"]//2*direction[0]
        end_y = self.touch_center[1]+self["boostSwipeSize"]//2*direction[1]

        start_x = self.touch_center[0]-self["boostSwipeSize"]/2*direction[0]
        start_y = self.touch_center[1]-self["boostSwipeSize"]//2*direction[1]
        #print("Direction is", direction)
        #print("Boost from ", start_x, start_y, "to", end_x, end_y)
        self.goto_relative(start_x, start_y)
        time.sleep(CONFIG["mouseResetWait"])
        pyautogui.mouseDown()
        time.sleep(CONFIG["mouseResetWait"])
        self.goto_relative(end_x, end_y)
        time.sleep(CONFIG["mouseResetWait"])
        self.reset_mouse()

name = "Metroid Prime Hunters"
mousefix = MPHMousefix
