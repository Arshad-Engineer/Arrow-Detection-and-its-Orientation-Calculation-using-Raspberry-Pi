'''
ENPM809T – Autonomous Robotics
Homework 4
Student Name: Arshad Shaik
UID: 118438832
Date: March 03, 2023
'''
# Import all packages
import numpy as np
import time
import cv2
import math
from datetime import datetime

from picamera.array import PiRGBArray
from picamera import PiCamera

# Initialize the Raspberry Pi camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 25
rawCapture = PiRGBArray(camera, size=(640,480))

# Allow the camera to warm-up
time.sleep(0.1)

# Create a VideoWriter object
result = cv2.VideoWriter('Arrow_Detection_Video.avi', cv2.VideoWriter_fourcc(*'MJPG'),25,(640,480))

# Initialize a frame numnber counter
fn = 1

# Open a file to save a frame processing time
f = open('Arrow_Detect.txt','a')

# Default state of Arrow Text
final_text = "-----"
text_counter = 0

# Video looping - for each image frame from the video, do the following:
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=False):
    
    # frame proccessing time - start time
    start_time = datetime.now() 
    
    # Read the image frame
    image = frame.array

    # Convert to BGR image to HSV image
    hsvIm = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the threshold values for HSV mask (Ref: colorpicker.py)
    minHSV = np.array([70, 50, 100]) #[30, 137, 0]
    maxHSV = np.array([100, 255, 255]) #[93, 255, 255]

    # Create a mask
    maskHSV = cv2.inRange(hsvIm, minHSV, maxHSV)

    # Blur the masked image before detecting the corners
    blurIm_unflt = cv2.GaussianBlur(maskHSV,(9,9),0)
    
    # Apply erosion to remove white noise and dilate to remove black noise
    kernel = np.ones((5,5), np.uint8)
    blurIm = cv2.erode(blurIm_unflt, kernel, iterations=1)
    blurIm = cv2.dilate(blurIm, kernel, iterations=1)
    
    # Convert the gray masked image into a color image
    blurImClr = cv2.cvtColor(blurIm, cv2.COLOR_GRAY2BGR)

    # Detect the top 5 corners using the cv2.goodFeaturesToTrack()
    # The top 2 corners will always be two most narrowed corners of the arrow head
    quality = 0.8 # varies from 0 to 1; close to 0 implies that even a slight corners are detected
    corners = cv2.goodFeaturesToTrack(blurIm,2,quality,10)
    len_corners = 0    
    if isinstance(corners, type(None)):
        print("\n Corners detected: 0")
        len_corners = 0
    else:
        print("\n Corners detected: ", len(corners))
        len_corners = len(corners)
      
    
    # Get the corners date to find the mid point of the arrow head
    if len_corners > 1 :
        
        print("\n Atleast 5 Corners detected: ")
        
                
        corners = np.int0(corners)
        
        # Iterate over the corners and draw a circle at that location
        for i in corners:
            x,y = i.ravel()
            cv2.circle(image,(x,y),10,(0,0,255),-1)
              
        for i in corners[0]:
            a0=i[0]
            b0=i[1]
        for i in corners[1]:
            a1=i[0]
            b1=i[1]
        #for i in corners[2]:
         #   a2=i[0]
          #  b2=i[1]
        #for i in corners[3]:
         #   a3=i[0]
          #  b3=i[1]
        #for i in corners[4]:
        #    a4=i[0]
        #    b4=i[1]

        # Find the mid-point of the arrow head
        am=(a0+a1)/2
        bm=(b0+b1)/2
        print(am,bm)

        # Draw a small dot the calculated midpoint of top 2 corners in blue color
        cv2.circle(image,  (int(am), int(bm)), 5, (255, 0, 0), -1)
         


        # Display all types of processed images from Camera Feed - [Original - HSV - Masked - Blurred]
        # cv2.namedWindow("Camera Feed - Original - HSV - Mask - blurImage", cv2.WINDOW_NORMAL)
        # cv2.imshow("Camera Feed - Original - HSV - Mask - blurImage", np.hstack([image, hsvIm, blurImClr, blurIm]))
        # cv2.resizeWindow("Camera Feed - Original - HSV - Mask - blurImage", 640, 480)

        #find the contour of the arrow
        (cont, _) = cv2.findContours(blurIm.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort the contours from contours with larger areas to smaller areas
        cont = sorted(cont, key = lambda x: cv2.contourArea(x), reverse=True)

        # when the contour is detected, draw a enclosing circle, line from center of the circle to 
        # calculate orinetation of the arraow, display it on the image

        if (len(cont[0]) > 0): # Contour with larger area, is our contour-of-interest

            #x, y, w, h = cv2.boundingRect(cont[i])

            # Find the minimum enclosing circle for the  biggest contour
            (x,y), radius = cv2.minEnclosingCircle(cont[0])

            # Draw a larger circle - minimum enclosing circle of the contour
            cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 3)

            # cv2.circle(image, (int(x), int(y)), 4, (0, 255, 0), 2)
                   
            # Drawing lines - from center of the circle to the mid-point of 
            # 1st two corners
            # Second one - from the center of the circle to the other end of the 
            #circle than the end of the above mid-point
            cv2.line(image, (int(x), int(y)), (int(am),int(bm)),(255,0,0),2)
            cv2.line(image, (int(x), int(y)), (int(radius+x),int(y)),(255,255,0),2)

            #Angles - slope = rise over run
            atan = math.atan2(int(bm)-int(y),int(am)-int(x))
            angle = math.degrees(atan)
            print ('angle=', angle)

            # Classify the orientation according to the angle and display it on the image
            if(angle >= -45 and angle < 45):
                #cv2.putText(image,'RIGHT', (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,255),10)
                #image, text, (300, 15), font, 1, red, 1)
                arrow_text = "RIGHT"
                print("RIGHT")
            elif(angle >=45 and angle < 135):
                #cv2.putText(image,'DOWN', (20, 100), cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),10)
                arrow_text = "DOWN"
                print("DOWN")
            elif(angle >= -180 and angle <=-135): 
                #cv2.putText(image,'LEFT', (20, 100), cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),10)
                arrow_text = "LEFT"
                print("LEFT")
            elif(angle >=135 and angle <=180):
                #cv2.putText(image,'LEFT', (20, 100), cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),10)
                arrow_text = "LEFT"
                print("LEFT")
            elif(angle > -135 and angle < -45):
                #cv2.putText(image,'UP', (20, 100), cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,0),10)
                arrow_text = "UP"
                print("UP")
                
            # Persistance time for change of arrow sign
            if (final_text != arrow_text):
                text_counter += 1
            else:
                text_counter = 0
            
            # Check for real change of sign
            if text_counter >= 5 :
                final_text = arrow_text
            
            # arrow text on screen final
            cv2.putText(image,final_text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),10)      
        
    # Display all types of processed images from Camera Feed - [Original - HSV - Masked - Blurred]
    cv2.namedWindow("Camera Feed - Original - HSV - Mask - blurImage - blurImageClr", cv2.WINDOW_NORMAL)
    cv2.imshow("Camera Feed - Original - HSV - Mask - blurImage - blurImageClr", np.hstack([image, hsvIm, blurImClr]))
    cv2.resizeWindow("Camera Feed - Original - HSV - Mask - blurImage - blurImageClr", 640, 480)
        # cv2.namedWindow("Camera Feed - Green Light Detection & Tracking", cv2.WINDOW_NORMAL)
        # cv2.imshow("Camera Feed - Green Light Detection & Tracking", image)
        # cv2.resizeWindow("Camera Feed - Green Light Detection & Tracking", 480, 320)
    
    # Save the image frame to the video file
    result.write(image)

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # calculate the end time all the processing for each frame
    fin_time = datetime.now()

    # Calculate the time lapsed for all the image processing so far, for each frame
    delta_time = fin_time - start_time

    # Open a file to save the frame processing time
    # f = open('Arrow_Detect.txt','a')

    # print time to run through loop to the screen & save to file
    # or keep appending to a list and write to a file all data at once
    outstring = str(delta_time.total_seconds()) + '\n'
    f.write(outstring)

    # print the time taken to process the frame
    print("Time taken to process the frame: ", delta_time.total_seconds())
    
    # f.close()
    # Print the frame number    
    print("\nframe: ", str(fn))

    # Increment the frame number
    fn += 1

    # Check if you give the value of 1000/25 = 40 for wiat key value and see if the video plays at normal rate
    key = cv2.waitKey(1) & 0xFF

    # press the 'q' key to exit
    if key == ord("q"):
        break

# Close all windows
cv2.destroyAllWindows()

# Close the opened file
f.close()