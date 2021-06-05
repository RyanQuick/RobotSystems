#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import numpy as np
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

AK = ArmIK()

range_rgb = {
    'red':   (0, 0, 255),
    'blue':  (255, 0, 0),
    'green': (0, 255, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
}


# The Closing angle of the gripper
servo1 = 500

# initial position
def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

def setBuzzer(timer):
    Board.setBuzzer(0)
    Board.setBuzzer(1)
    time.sleep(timer)
    Board.setBuzzer(0)

def move_thread(m):
    m.pickup_cube()
    
#set the rgb light color of the expansion board to make it consistent with the color to be tracked
def set_rgb(color):
    if color == "red":
        Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
        Board.RGB.show()
    elif color == "green":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
        Board.RGB.show()
    elif color == "blue":
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
        Board.RGB.show()
    else:
        Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
        Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
        Board.RGB.show()

class Sensing:
    def __init__(self):
        self.roi = ()
        self.rect = None
        self.count = 0
        self.get_roi = False
        self.center_list = []
        self.unreachable = False
        self.isRunning = True
        self.start_pick_up = False
        self.rotation_angle = 0
        self.last_x = 0
        self.last_y = 0
        self.world_X = 0
        self. world_Y = 0
        self. start_count_t1 = True
        self.t1 = 0
        self.detect_color = 'None'
        self.draw_color = range_rgb["black"]
        self.color_list = []
        self.size = (640,480)
        self.target_color = ('red', 'green', 'blue')
       
    def pull_image(self, img):
        '''
        INPUT: image file
        OUTPUT: modified, original image
        Grabs current image, draws crosshairs, and filters colors
        '''
        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)


        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #If an area is detected with a recognized object, it will always be detected until there is no
        if self.get_roi and not self.start_pick_up:
            self.get_roi = False
            frame_gb = getMaskROI(frame_gb, self.roi, self.size)      
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert Image to Lab Space
        return frame_lab, img
    
    #Find the contour with the largest area
    #Parameter is list of contours to compare
    def get_area_max_contour(self,contours):
        '''
        INPUT: Outlines/contours from cv
        OUTPUT: Largest outline & area
        Calculated largest area from all found contours
        '''
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours :
            contour_area_temp = math.fabs(cv2.contourArea(c))  #Calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  #Only when the area is greater than 300, the contour of the largest area is effective to filter interferance 
                    area_max_contour = c

        return area_max_contour, contour_area_max  #Return the largest contour

    
    def biggest_area(self,frame_lab):
        '''
        INPUT: Modified image from earlier
        OUTPUT: Largest outline, area, and color
        Calculated largest area from all found contours & color
        '''
        
        if not self.start_pick_up:
            color_area_max = None
            max_area = 0
            areaMaxContour_max = [0,0]
            for i in color_range:
                
                if i in self.target_color:
                    frame_mask = cv2.inRange(frame_lab, color_range[i][0], color_range[i][1])  #perform bit operations on the original
                    opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6,6),np.uint8))  #open operation
                    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6,6),np.uint8))#closed operation
                    contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  #Find the Outline
                    areaMaxContour, area_max = self.get_area_max_contour(contours)  #Find the largest contour
                    if areaMaxContour is not None:
                        if area_max > max_area:# Find the largest area
                            max_area = area_max
                            color_area_max = i
                            areaMaxContour_max = areaMaxContour
            return areaMaxContour_max, max_area, color_area_max

                            
    def draw_outline_color(self, img, areaMaxContour_max, max_area, color_area_max):
        '''
        INPUT: Contour Area from last function, original image to draw on
        OUTPUT: x,y in world coordinates of shape
        Calculated largest area from all found contours & color
        '''
        if not self.start_pick_up:
            self.rect = cv2.minAreaRect(areaMaxContour_max)
            box = np.int0(cv2.boxPoints(self.rect))
            self.roi = getROI(box) #Get ROI Area 
            self.get_roi = True
            self.img_centerx, self.img_centery = getCenter(self.rect, self.roi, self.size, square_length)  # Get the center coordinates of the wood block
             
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) #Convert to real world Coordinates
            cv2.drawContours(img, [box], -1, range_rgb[color_area_max], 2)
            cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[color_area_max], 1) #Draw the center point
            return world_x, world_y
            
    def set_color(self, color_area_max):
        '''
        INPUT: Color string
        OUTPUT: ___
        Converts color string to int
        '''
        if not self.start_pick_up:
            if color_area_max == 'red':  #red max
                color = 1
            elif color_area_max == 'green':  #green max
                color = 2
            elif color_area_max == 'blue':  #blue max 
                color = 3
            else:
                color = 0
            self.color_list.append(color)
                    
    def position_confidence(self, world_x, world_y):
        '''
        INPUT: x,y in world coordinates of shape
        OUTPUT: ___
        Sets self.variables depending on how far the center of the shape moved since last check
        Counter counts when shape hasn't moved
        Used to decide when to start grasp
        '''
        
        
        distance = math.sqrt(pow(world_x - self.last_x, 2) + pow(world_y - self.last_y, 2)) #Compare the last coordinate to determine whether to move 
        self.last_x, self.last_y = world_x, world_y     
        # Cumulative judgement 
        if distance < 0.5:
            self.count += 1
            self.center_list.extend((world_x, world_y))
            if self.start_count_t1:
                self.start_count_t1 = False
                self.t1 = time.time()
            if time.time() - self.t1 > 1:
                rotation_angle = self.rect[2] 
                self.start_count_t1 = True
                self.world_X, self.world_Y = np.mean(np.array(self.center_list).reshape(self.count, 2), axis=0)
                self.center_list = []
                self.count = 0
                self.start_pick_up = True
        else:
            self.t1 = time.time()
            self.start_count_t1 = True
            self.center_list = []
            self.count = 0
        
    def set_text_color(self, color_area_max):
        '''
        INPUT: Color string
        OUTPUT: ___
        Sets the color of the bottom left text
        '''
        self.set_color(color_area_max)
        if len(self.color_list) == 3:  #Multiple Judgements
            # take the average
            color = int(round(np.mean(np.array(self.color_list))))
            self.color_list = []
            if color == 1:
                self.detect_color = 'red'
                self.draw_color = range_rgb["red"]
            elif color == 2:
                self.detect_color = 'green'
                self.draw_color = range_rgb["green"]
            elif color == 3:
                self.detect_color = 'blue'
                self.draw_color = range_rgb["blue"]
            else:
                self.detect_color = 'None'
                self.draw_color = range_rgb["black"]
            print("first seen color",self.detect_color)                
 
 

class Moving():
    def __init__(self,s):
        self.s = s
        self.stop = False
        self.unreachable = True
        self.rotation_angle = 0
        self.num_cubes = 0
        self.goal = [0,0]
        self.target = [0,0]
        self.height = 1.5
        self.orientation = 0

    def stacking_cube(self, goal_coordinate):
        '''
        x,y,z,orientation of each cube
        i take those and do things
        '''
        while True:
            self.num_cubes = len(self.s.cube_pose)
            # how many objects do i have?
            if self.num_cubes == 3:
                dist = np.sqrt((self.s.img_centerx - self.s.cube_pose['red'][0])**2 + (self.s.img_centery - self.s.cube_pose['red'][1])**2)
                if dist < 1.5:
                    # this means red is in the middle and we should move to blue
                    self.height = 4.5
                    self.goal = [self.s.cube_pose['blue'][0], self.s.cube_pose['blue'][1]]
                    self.target = [self.s.cube_pose['red'][0], self.s.cube_pose['red'][1]]
                    self.orientation = self.s.cube_pose['blue'][3]
                    self.rgb('blue')
                else:
                    # red first
                    self.goal = [self.s.cube_pose['red'][0], self.s.cube_pose['red'][1]]
                    self.target = [self.s.img_centerx, self.s.img_centery]
                    self.orientation = self.s.cube_pose['red'][3]
                    self.rgb('red')
            elif self.num_cubes == 2:
                # green last
                self.height = 7.5
                self.goal = self.s.cube_pose['green'][0], self.s.cube_pose['green'][1]
                self.target = [self.s.cube_pose['blue'][0], self.s.cube_pose['blue'][1]]
                self.orientation = self.s.cube_pose['green'][3]
                self.rgb('green')
            elif self.num_cubes == 1:
                # Return to the initial position
                initMove()  
                time.sleep(1.5)

            setBuzzer(0.1)
            # find first goal
            result = AK.setPitchRangeMoving((self.goal[0], self.goal[1], 7), -90, -90, 0)  
            if result == False:
                self.unreachable = True
            else:
                self.unreachable = False
                time.sleep(result[2]/1000) #If you can reach the specified location, get the running time
                # angle for gripper to be rotated to not be in the way
                servo2_angle = getAngle(self.goal[0], self.goal[1], self.orientation)
                Board.setBusServoPulse(1, servo1 - 280, 500)  # Paws Open
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.5)
                # move down to height
                AK.setPitchRangeMoving((self.goal[0], self.goal[1], self.height), -90, -90, 0, 1000)
                time.sleep(1.5)
                # holder closure 
                Board.setBusServoPulse(1, servo1, 500) 
                time.sleep(0.8)
                # close and lift up
                Board.setBusServoPulse(2, 500, 500)
                AK.setPitchRangeMoving((self.goal[0], self.goal[1], 12), -90, -90, 0, 1000)
                time.sleep(1)
                # move to target position at 12 height
                result = AK.setPitchRangeMoving((self.target[0], self.target[1], 12), -90, -90, 0)   
                time.sleep(result[2]/1000)
                # move to orientation of target
                servo2_angle = getAngle(self.target[0], self.target[1], self.orientation)
                Board.setBusServoPulse(2, servo2_angle, 500)
                time.sleep(0.5)
                # drop to slightly above height
                AK.setPitchRangeMoving((self.target[0], self.target[1], self.height+3), -90, -90, 0, 500)
                time.sleep(0.5)
                # drop to right height
                AK.setPitchRangeMoving((self.target[0], self.target[1], self.height), -90, -90, 0, 1000)
                time.sleep(0.5)
                # Open the Claws, Put down the object
                Board.setBusServoPulse(1, servo1 - 200, 500)
                time.sleep(0.8)
                # lift back up some
                AK.setPitchRangeMoving((self.target[0], self.target[1], 12), -90, -90, 0, 800)
                time.sleep(0.8)
                # Return to the initial position
                initMove()  
                time.sleep(1.5)                

                    
    def pickup_cube(self):
        #place coordinates
        coordinate = {
         'red':   (-15 + 0.5, 12 - 0.5, 1.5),
         'green': (-15 + 0.5, 6 - 0.5,  1.5),
         'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        while True:
            if self.s.isRunning:
                
                
                if self.s.detect_color != 'None' and self.s.start_pick_up:  #if it is detected that the block has not moved for a period of time, start to pick up. 
                    print("Picking up ", self.s.detect_color)                    #Move to the target position, height 6cm, judge whether the pos can be reached by the returned result
                    #If the running time parameter is not given it will automatically be calculated and returned by the result.
                    set_rgb(self.s.detect_color)
                    setBuzzer(0.1)
                    result = AK.setPitchRangeMoving((self.s.world_X, self.s.world_Y, 7), -90, -90, 0)  
                    if result == False:
                        self.unreachable = True
                    else:
                        self.unreachable = False
                        time.sleep(result[2]/1000) #If you can reach the specified location, get the running time

                        if not self.s.isRunning:
                            continue
                        servo2_angle = getAngle(self.s.world_X, self.s.world_Y, self.rotation_angle) #Calculate the angle the gripper needs to be rotated
                        Board.setBusServoPulse(1, servo1 - 280, 500)  # Paws Open
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.s.isRunning:
                            continue
                        AK.setPitchRangeMoving((self.s.world_X, self.s.world_Y, 1.5), -90, -90, 0, 1000)
                        time.sleep(1.5)

                        if not self.s.isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1, 500) # holder closure 
                        time.sleep(0.8)

                        if not self.s.isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        AK.setPitchRangeMoving((self.s.world_X, self.s.world_Y, 12), -90, -90, 0, 1000)  #Mechanical arm lift up
                        time.sleep(1)

                        if not self.s.isRunning:
                            continue
                        result = AK.setPitchRangeMoving((coordinate[self.s.detect_color][0], coordinate[self.s.detect_color][1], 12), -90, -90, 0)   
                        time.sleep(result[2]/1000)

                        if not self.s.isRunning:
                            continue                   
                        servo2_angle = getAngle(coordinate[self.s.detect_color][0], coordinate[self.s.detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.s.isRunning:
                            continue
                        AK.setPitchRangeMoving((coordinate[self.s.detect_color][0], coordinate[self.s.detect_color][1], coordinate[self.s.detect_color][2] + 3), -90, -90, 0, 500)
                        time.sleep(0.5)

                        if not self.s.isRunning:
                            continue                    
                        AK.setPitchRangeMoving((coordinate[self.s.detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)

                        if not self.s.isRunning:
                            continue
                        Board.setBusServoPulse(1, servo1 - 200, 500)  # Open the Claws, Put down the object
                        time.sleep(0.8)

                        if not self.s.isRunning:
                            continue
                        AK.setPitchRangeMoving((coordinate[self.s.detect_color][0], coordinate[self.s.detect_color][1], 12), -90, -90, 0, 800)
                        time.sleep(0.8)

                        initMove()  # Return to the initial position
                        time.sleep(1.5)

                        self.s.detect_color = 'None'
                        self.s.get_roi = False
                        self.s.start_pick_up = False
                        set_rgb(self.s.detect_color)
            else:
                if self.stop:
                    self.stop = False
                    Board.setBusServoPulse(1, servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)


if __name__ == '__main__':
    initMove() # Move to starting position
    s = Sensing() # Initialize classes
    m = Moving(s)

    # Run Child Thread
    th = threading.Thread(target=move_thread, args=(m,))
    th.setDaemon(True)
    th.start()
    
    # Start Camera
    my_camera = Camera.Camera()
    my_camera.camera_open()
    
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            p_frame, Frame = s.pull_image(frame)
            if not s.start_pick_up:
                areaMaxContour_max, max_area, color_area_max = s.biggest_area(p_frame)
            if max_area > 2500:  # Found the largest area
                if not s.start_pick_up:
                    world_x, world_y = s.draw_outline_color(Frame, areaMaxContour_max, max_area, color_area_max)
                if not s.start_pick_up:    
                    s.position_confidence(world_x, world_y)
                if not s.start_pick_up:
                    s.set_text_color(color_area_max)
                    
            # Draw text for seen object
            cv2.putText(Frame, "Color: " + s.detect_color, (10, Frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, s.draw_color, 2)
            cv2.imshow('Frame', Frame)
            set_rgb(s.detect_color)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
