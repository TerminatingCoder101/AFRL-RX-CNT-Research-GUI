import rpicam
import cv2
import time

class CameraStream:
    def __init__(self, ip, user, password, shutter_speed, iso):
        self.ip = ip
        self.user = user
        self.password = password
        self.shutter_speed = shutter_speed
        self.iso = iso
        self.running = False
        self.cap = None
        self.video_label = None  # Initialize this with your actual video label object
        self.cam = rpicam.Camera()

    def start(self):
        self.running = True
        self.update_raspberry_pi_frame()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def update_raspberry_pi_frame(self):
        while self.running:
            try:
                # Configure the camera
                self.cam.config(
                    shutter_speed=self.shutter_speed,
                    iso=self.iso
                )
                self.cam.start_recording('udp://0.0.0.0:2222')

                time.sleep(2)
                self.cap = cv2.VideoCapture(f"udp://{self.ip}:2222")

                if self.cap.isOpened():
                    print("Connected to RPi Camera")
                else:
                    print("Not connected to RPi Camera")
                
                while self.cap.isOpened() and self.running:
                    ret, frame = self.cap.read()
                    if ret:
                        # Assuming your video_label is a tkinter Label or similar widget
                        self.video_label.imgtk = frame
                        self.video_label.configure(image=self.video_label.imgtk)
                    else:
                        break

                self.cam.stop_recording()
            except Exception as e:
                print(f"Failed to update frame from Raspberry Pi Camera: {e}")
                break