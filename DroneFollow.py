import djitellopy as tello
import cv2
from cvzone.PoseModule import PoseDetector
import time


def main():

    # Parameters
    #######################################################
    width = 320       # Width of image
    height = 240      # Height of image
    startCounter = 0  # 0 for flight 1 for testing
    #######################################################

    print("start")
    # Connect to Tello
    me = tello.Tello()
    me.connect()

    me.for_back_velocity = 0
    me.left_right_velocity = 0
    me.up_down_velocity = 0
    me.yaw_velocity = 0
    me.speed = 0

    print(me.get_battery())

    me.streamoff()
    me.streamon()

    detector = PoseDetector(staticMode=False, modelComplexity=1, smoothLandmarks=True, enableSegmentation=False,
                        smoothSegmentation=True, detectionCon=0.5, trackCon=0.5)
    
    # TAKEOFF in beginning
    if startCounter == 0:
        me.takeoff()
        time.sleep(3)
        startCounter = 1

    # MAIN RUN LOOP
    while True:

        # Get image from Tello
        frame_read = me.get_frame_read()
        myFrame = frame_read.frame
        img = cv2.resize(myFrame, (width, height))

        
        img = detector.findPose(img)

        lmList, bboxInfo = detector.findPosition(img, draw=True, bboxWithHands=False)

        #(80,60), (240,180) # Fix vars (lowB = height*2/5)
        cv2.rectangle(img, (120,100), (200,180),color=(255, 255, 255))

        # Get CENTER
        if lmList:
            center = bboxInfo["center"]
            cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
            print(center)

            # 1. Keep center in middle box (turn/rotate)
            x,y = center[0], center[1]

            if x < 120:
                me.rotate_counter_clockwise(10)
                time.sleep(.1)
            elif x > 200:
                me.rotate_clockwise(10)
                time.sleep(.1)

            if y < 100:
                me.move_up(20)
                time.sleep(.1)
            elif y > 180:
                me.move_down(20)
                time.sleep(.1)

            # 2. If Handsign
            cnt = 0
            rHandElbow = []
            rHandWrist = []
            for keyPoint in lmList:
                #print(keyPoint)
                if cnt == 14:
                    rHandElbow = keyPoint
                if cnt == 16:
                    rHandWrist = keyPoint
                cnt += 1

            c = 0
            rHandY = 0
            rHandX = 0
            rElbowX = 0
            rElbowY = 0
            for kp in rHandWrist:
                if c == 0:
                    rHandX = kp
                if c == 1:
                    rHandY = kp
                    break
                c += 1
            c = 0
            for kp in rHandElbow:
                if c == 0:
                    rElbowX = kp
                if c == 1:
                    rElbowY = kp
                    break
                c += 1

            if rHandY < rElbowY:
               if rHandX > rElbowX:
                   me.move_right(20)
                   time.sleep(.1)
               elif rHandX < rElbowX:
                   me.move_left(20)
                   time.sleep(.1)
 

        else:

            # 0. 360 in place to find body
            me.rotate_clockwise(20)
            time.sleep(.1)
            pass

        
        # Display image
        cv2.imshow("MyResult", img)

        # Wait for "Q" button to stop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()
            break

if __name__ == "__main__":
    main()