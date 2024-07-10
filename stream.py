from picamera2 import Picamera2
from libcamera import controls
from PIL import Image
import numpy as np
import socket
import time
import io
import argparse

def start_stream(ip_addr, shutter_speed, iso_value):
    picam2 = Picamera2()
    iso_value1 = int(iso_value)
    shutter_speed1 = int(shutter_speed)
    ag = (iso_value1 / 100)
    config = picam2.create_video_configuration(
        main={"size": (1080, 1080)},
        controls = {
            "ExposureTime": shutter_speed1,  # in microseconds
            "AnalogueGain": ag,
            #"Brightness": 0.4,             
            #"Saturation": 0,   
            #"Sharpness": 0,       
            "AwbEnable": False,
            "AwbMode": controls.AwbModeEnum.Custom,
            #"ColourGains": (3.4795,1.1079),
            "AeMeteringMode": controls.AeMeteringModeEnum.CentreWeighted
        }
    )

    picam2.configure(config)
    picam2.start()

    #time.sleep(5)  # Camera warm-up time
    # Set up UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Starting camera stream...")
    time_delay = 0
    local_image_path = '/home/pi/AFRL_RX_GUI/temp_rpicam_img.npy'
    try:
        while True:
            buffer = io.BytesIO()
            picam2.capture_file(buffer, format='jpeg')
            buffer.seek(0)
            #image_data = buffer.read()
            image = Image.open(buffer)
            resized_image = image.resize((400, 400), Image.LANCZOS)
            resized_buffer = io.BytesIO()
            resized_image.save(resized_buffer, format='jpeg')
            resized_buffer.seek(0)

            if time_delay < 5:
                request = picam2.capture_request()
                img_arr = request.make_array("main")
                np.save(local_image_path, img_arr)
                print("HD Image captured and saved locally")
                request.release()
                time_delay+=1
            else:
                time_delay = 0

            client_socket.sendto(resized_buffer.read(), (ip_addr, 8000))
        
            print("Frame sent")
            time.sleep(0.1)  # Adjust this as needed to control frame rate
    finally:
            picam2.stop()






if __name__ == '__main__':
    print("Script started")
    parser = argparse.ArgumentParser()
    parser.add_argument("ipaddr", help="The IP address of the local machine")
    parser.add_argument("shutter_speed", help="The shutter speed")
    parser.add_argument("iso_value", help="The iso ")
    args = parser.parse_args()
    ip_addr = args.ipaddr
    shutter_speed = args.shutter_speed
    iso_value = args.iso_value
    start_stream(ip_addr, shutter_speed, iso_value)