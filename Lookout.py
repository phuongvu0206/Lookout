import os
import datetime
import logging
import cv2
import time

import util
# Rename "Silent-Face-Anti-Spoofing" to "SFAS" for easier import
# from SFAS.test import test

import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

import email_settings
from email_settings import password, from_email, to_email, HOST, PORT
if from_email == "" or password == "":
    from_email = email_settings.from_email_default
    password = email_settings.password_default

# Configure logging
logging.basicConfig(filename="log_lookout.log",
                    level=logging.INFO, format='%(asctime)s - %(message)s')


def send_email(to_email, from_email, body, image_path=None):
    # Create server
    server = smtplib.SMTP(HOST, PORT)
    server.starttls()

    # Login Credentials for sending the email
    server.login(from_email, password)

    message = MIMEMultipart()
    message['Subject'] = "Laptop Alert"
    message['From'] = from_email
    message['To'] = to_email
    message['Cc'] = from_email
    message['Bcc'] = from_email

    message.attach(MIMEText(body, 'plain'))

    # Attach image if provided
    if image_path:
        image = open(image_path, "rb").read()
        message.attach(MIMEImage(image))

    server.sendmail(from_email, to_email, message.as_string())
    server.quit()


class Lookout:
    def __init__(self):
        self.db_dir = "db"
        self.log_path = "log.txt"
        self.spoofing_model_dir = "./SFAS/resources/anti_spoof_models"
        self.email_sent = False
        self.cap = cv2.VideoCapture(0)

        # Reduce resolution for faster runtime
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Variables for spoofing model
        self.spoof_test_function = None
        self.spoof_model_loaded = False
        self.spoof_model_error = False
        self._load_spoof_model_async()  # Load model in the background

    def _load_spoof_model_async(self):
        def load():
            try:
                from SFAS.test import test
                self.spoof_test_function = test
                self.spoof_model_loaded = True
            except Exception as e:
                self.spoof_model_error = True
                logging.error(f"Load model failed: {str(e)}")
        
        threading.Thread(target=load).start()      

    # def check_identity(self):
    #     # Capture frames for 1 seconds
    #     start_time = time.time()
    #     frames = []

    #     while (time.time() - start_time) < 1:
    #         if not self.cap.isOpened():
    #             logging.error("Failed to open webcam")
    #             return

    #         ret, frame = self.cap.read()
    #         if not ret:
    #             logging.error("Failed to capture frame")
    #             return
    #         frames.append(frame)
        
    #     self.cap.release()

    #     # Use last frame for detection
    #     if frames:
    #         final_frame = frames[-1]
    #         return self.process_frame(final_frame)

    def check_identity(self):
        if not self.cap.isOpened():
            logging.error("Failed to open webcam")
            return

        ret, frame = self.cap.read()
        if not ret:
            logging.error("Failed to capture frame")
            return
        else:
            return self.process_frame(frame)

    def process_frame(self, frame):
        # Model not loaded yet
        if not self.spoof_model_loaded and not self.spoof_model_error:
            logging.warning("Model still loading, waiting...")
            time.sleep(2)
        
        # Model loaded but encountered an error
        if self.spoof_model_error:
            logging.error("Using fallback check due to model error")
            return
        
        # Model loaded successfully
        label = self.spoof_test_function(
            image=frame,
            model_dir=self.spoofing_model_dir,
            device_id=0
        )
        # label = test(
        #     image=frame,
        #     model_dir=self.spoofing_model_dir,
        #     device_id=0
        # )

        if label == 1:  # Real face
            name = util.recognize(frame, self.db_dir)
            if name in ["unknown_person", "no_persons_found"]:
                logging.warning("Unknown person detected!")
                self.handle_unknown_person(frame)
            else:
                logging.info(f"Welcome {name}")
                self.log_access(name)
        else:
            logging.warning("Spoofing detected!")
            self.handle_spoofing(frame)

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()

    def handle_unknown_person(self, frame):
        sus_img_path = os.path.join(self.db_dir, "unknown_person.jpg")
        cv2.imwrite(sus_img_path, frame)
        threading.Thread(
            target=self._send_email_with_cleanup,
            args=(sus_img_path, "Unknown person detected!")
        ).start()

    def handle_spoofing(self, frame):
        sus_img_path = os.path.join(self.db_dir, "spoofing_detected.jpg")
        cv2.imwrite(sus_img_path, frame)
        threading.Thread(
            target=self._send_email_with_cleanup,
            args=(sus_img_path, "Spoofing detected!")
        ).start()

    def _send_email_with_cleanup(self, img_path, message):
        send_email(to_email, from_email, message, img_path)
        os.remove(img_path)  # Delete image after sending email

    def log_access(self, name):
        with open(self.log_path, "a") as f:
            f.write(f"User: {name}, Datetime: {datetime.datetime.now()}\n")

    def run(self):
        self.check_identity()


logging.info("Script started")
service = Lookout()
service.run()
logging.info("Script finished")
