from picamera2 import Picamera2
from libcamera import controls
from PIL import Image
import socket
import time
import io
import argparse
import threading


class CameraStreamer:
    def __init__(self, ip_addr, shutter_speed, iso_value):
        self.ip_addr = ip_addr
        self.shutter_speed = int(shutter_speed)
        self.iso_value = int(iso_value)
        self.running = False
        self.hdpic_thread = None

    def start_stream(self):
        self.picam2 = Picamera2()
        iso_value1 = int(self.iso_value)
        shutter_speed1 = int(self.shutter_speed)
        ag = (iso_value1 / 100) * 2.317
        config = self.picam2.create_video_configuration(
            main={"size": (1920, 1080)},
            controls = {
                "ExposureTime": shutter_speed1,  # in microseconds
                "AnalogueGain": ag,
                # "Brightness": 0.4,             
                # "Saturation": 0,   
                # "Sharpness": 0,       
                "AwbEnable": False,
                "AwbMode": controls.AwbModeEnum.Custom,
                #"ColourGains": (3.4795,1.1079),
                "AeMeteringMode": controls.AeMeteringModeEnum.CentreWeighted
            }
        )
        self.picam2.configure(config)
        self.picam2.start()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.running = True
        hdpic_thread = threading.Thread(target=self.capt_hd_img)
        hdpic_thread.start()
        #time.sleep(5)  # Camera warm-up time

        # Set up UDP socket
        

        print("Starting camera stream...")

        try:
            while True:
                buffer = io.BytesIO()
                self.picam2.capture_file(buffer, format='jpeg')
                # metadata = self.picam2.capture_metadata()
                # print(metadata)
                buffer.seek(0)

                image = Image.open(buffer)
                resized_image = image.resize((400, 400), Image.LANCZOS)
                resized_buffer = io.BytesIO()
                resized_image.save(resized_buffer, format='jpeg')
                resized_buffer.seek(0)

                client_socket.sendto(resized_buffer.read(), (self.ip_addr, 8000))
                print("Frame sent")
                time.sleep(0.1)  # Adjust this as needed to control frame rate
        finally:
                self.picam2.stop()

    def capt_hd_img(self):
        while self.running:
            #self.picam2.create_still_configuration(main={"size": (1920, 1080)})
            buffer = io.BytesIO()
            self.picam2.capture_file(buffer, format='jpeg')
            buffer.seek(0)
            image_data = buffer.read()
            # Save the image locally
            local_image_path = '/home/pi/AFRL_RX_GUI/temp_rpicam_img.png'
            with open(local_image_path, 'wb') as f:
                f.write(image_data)
            print("HD Image captured and saved locally")
            time.sleep(5000)

    def close(self):
        self.running = False
        if self.hdpic_thread is not None:
            self.hdpic_thread.join()
        self.picam2.stop()
        print("Camera and threads closed")


if __name__ == '__main__':
    print("Script started")
    parser = argparse.ArgumentParser()
    parser.add_argument("ipaddr", help="The IP address of the local machine")
    parser.add_argument("shutter_speed", help="The shutter speed")
    parser.add_argument("iso_value", help="The iso ")
    args = parser.parse_args()
    streamer = CameraStreamer(args.ipaddr, args.shutter_speed, args.iso_value)
    try:
        streamer.start_stream()
    except KeyboardInterrupt:
        streamer.close()


