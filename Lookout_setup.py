import os
import logging
import pickle
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition

import util
# Rename "Silent-Face-Anti-Spoofing" to "SFAS" for easier import
from SFAS.test import test

import smtplib
import email_settings

# Set up the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(filename=os.path.join(BASE_DIR, "log_lookout.log"),
                    level=logging.INFO, format='%(asctime)s - %(message)s')


class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.configure(background="#f2f3f1")
        self.main_window.geometry("550x300+570+300")  # width x height + x + y
        self.main_window.title("Lookout Setup")

        # Message
        introduction_text = "Welcome to Lookout!"
        self.introduction_message = util.get_message(self.main_window, introduction_text, width=340, background="#f2f3f1", foreground="black", font=("Segoe UI", 24, "bold"))
        self.introduction_message.place(relx=0.2, rely=0.05, relheight=0.2, relwidth=0.618)


        # Buttons
        self.check_user_button_main_window = util.get_button(
            self.main_window, "Email Setup", "#02a5a7", self.set_up_email, fg="white")
        self.check_user_button_main_window.place(relx=0.055, rely=0.3, height=50, width=490)

        self.register_button_main_window = util.get_button(
            self.main_window, "Face Registration", "#02a5a7", self.face, fg="white")
        self.register_button_main_window.place(relx=0.055, rely=0.517, height=50, width=490)

        self.exit_button_main_window = util.get_button(
            self.main_window, "Exit", "#f58a1d", self.exit, fg="white")
        self.exit_button_main_window.place(relx=0.055, rely=0.733, height=50, width=490)


        # Set up database directory
        self.db_dir = os.path.join(BASE_DIR, "db")
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)

        # Set up spoofing model directory
        self.spoofing_model_dir = os.path.join(BASE_DIR, "SFAS", "resources", "anti_spoof_models")


    def set_up_email(self):
        """ Set up email for sending notifications.
        """
        self.set_up_email_window = tk.Toplevel(self.main_window)
        self.set_up_email_window.configure(background="#f2f3f1")
        self.set_up_email_window.geometry(
            "550x500+575+200")
        self.set_up_email_window.title("Set Up Email")

        # Message (Instructions)        
        self.instruction_labelframe = tk.LabelFrame(
            self.set_up_email_window,
            text="Instructions",
            font=("Segoe UI bold", 9),
            background="#f2f3f1",
            foreground="#545454"
        )
        self.instruction_labelframe.place(relx=0.073, rely=0.02, relheight=0.168, relwidth=0.856)
        
        instruction_text = "Sender Email: The email used to send alerts. Requires a passcode. If left blank, a default email will be used.\nRecipient Email: The email that will receive the alerts."
        self.instruction_message = util.get_message(self.set_up_email_window, instruction_text, width=450, background="#f2f3f1", foreground="#545454", font=("Segoe UI", 9))
        self.instruction_message.place(relx=0.109, rely=0.059, relheight=0.099, relwidth=0.783)

        # Text & Entry
        self.sender_text_label_set_up_email = util.get_text_label(
            self.set_up_email_window, "Sender Email (Optional):", "#f2f3f1", font=("Segoe UI", 14, "bold"))
        self.sender_text_label_set_up_email.place(relx=0.073, rely=0.217, relheight=0.059, relwidth=0.474)

        self.sender_entry_set_up_email = util.get_entry_text(
            self.set_up_email_window)
        self.sender_entry_set_up_email.place(relx=0.073, rely=0.296, height=50, relwidth=0.856)

        self.password_text_label_set_up_email = util.get_text_label(
            self.set_up_email_window, "Sender Email's Password:", "#f2f3f1", font=("Segoe UI", 14, "bold"))
        self.password_text_label_set_up_email.place(relx=0.073, rely=0.415, relheight=0.059, relwidth=0.474)

        self.password_entry_set_up_email = util.get_entry_text(
            self.set_up_email_window)
        self.password_entry_set_up_email.place(relx=0.073, rely=0.494, height=50, relwidth=0.856)

        self.recipient_text_set_up_email = util.get_text_label(
            self.set_up_email_window, "Recipient Email:", "#f2f3f1", font=("Segoe UI", 14, "bold"))
        self.recipient_text_set_up_email.place(relx=0.073, rely=0.613, relheight=0.059, relwidth=0.364)

        self.recipient_entry_set_up_email = util.get_entry_text(
            self.set_up_email_window)
        self.recipient_entry_set_up_email.place(relx=0.073, rely=0.692, height=50, relwidth=0.856)
        
        # Buttons
        self.register_button_set_up_email_window = util.get_button(
            self.set_up_email_window, "Register", "#02a5a7", self.register_set_up_email, fg="white")
        self.register_button_set_up_email_window.place(relx=0.528, rely=0.85, height=50, width=220)
        
        self.back_button_set_up_email_window = util.get_button(
            self.set_up_email_window, "Back", "#f58a1d", lambda: self.set_up_email_window.destroy(), fg="white")
        self.back_button_set_up_email_window.place(relx=0.073, rely=0.85, height=50, width=220)

        
    def register_set_up_email(self):
        """ Process the email registration of a new user.
        """
        sender_email = self.sender_entry_set_up_email.get(1.0, "end-1c")
        password = self.password_entry_set_up_email.get(1.0, "end-1c")
        receiver_email = self.recipient_entry_set_up_email.get(1.0, "end-1c")

        if receiver_email == "":
            util.msg_box("Error!", "Please enter Recipient Email!", parent=self.set_up_email_window)
            return
        email_settings.to_email = receiver_email

        if sender_email != "" and password != "":
            email_settings.from_email = sender_email
            email_settings.password = password
        else:
            email_settings.from_email = email_settings.from_email_default
            email_settings.password = email_settings.password_default

        # Create server & Try to login
        server = smtplib.SMTP(email_settings.HOST, email_settings.PORT)
        server.starttls()
        try:
            server.login(email_settings.from_email, email_settings.password)
        except smtplib.SMTPAuthenticationError as e:
            util.msg_box("Error!", "Invalid Sender Email or Password!", parent=self.set_up_email_window)
            server.quit()
            return

        util.msg_box("Success!", "Email set up successfully!", parent=self.set_up_email_window)

        # Save email settings to file
        with open(os.path.join(BASE_DIR, "email_settings.py"), "r") as f:
            lines = f.readlines()

        with open(os.path.join(BASE_DIR, "email_settings.py"), "w") as file:
            for line in lines:
                if line.strip().startswith("to_email ="):
                    file.write(f'to_email = "{email_settings.to_email}"\n')
                elif line.strip().startswith("from_email ="):
                    file.write(f'from_email = "{email_settings.from_email}"\n')
                elif line.strip().startswith("password ="):
                    file.write(f'password = "{email_settings.password}"\n')
                else:
                    file.write(line)

        server.quit()


    def face(self):
        self.face_window = tk.Toplevel(self.main_window)
        self.face_window.configure(background="#f2f3f1")
        self.face_window.geometry("960x540+400+150")
        self.face_window.title("Face Registration")

        # Buttons
        self.check_user_button_face_window = util.get_button(
            self.face_window, "Check User", "#02a5a7", self.check_user, fg="white")
        self.check_user_button_face_window.place(relx=0.707, rely=0.581, height=50, width=240)

        self.register_button_face_window = util.get_button(
            self.face_window, "Register New User", "#daf2f2", self.register_new_user, fg="#02a5a7")
        self.register_button_face_window.place(relx=0.707, rely=0.71, height=50, width=240)

        self.back_button_face_window = util.get_button(
            self.face_window, "Back", "#f58a1d", lambda: self.face_window.destroy(), fg="white")
        self.back_button_face_window.place(relx=0.707, rely=0.839, height=50, width=240)

        # Label
        self.frame_face_window = tk.Frame(self.face_window, background="#02a5a7")
        self.frame_face_window.place(relx=0.031, rely=0.074, height=463, width=604)

        self.webcam_label = util.get_img_label(self.face_window)
        self.webcam_label.place(relx=0.043, rely=0.092, height=442, width=581)

        self.add_webcam(self.webcam_label)

        # Message
        introduction_text = "This app creates user accounts for laptop access."
        self.introduction_message = util.get_message(self.face_window, introduction_text, width=240, background="#f2f3f1", foreground="gray")
        self.introduction_message.place(relx=0.707, rely=0.065, height=60, width=240)

        self.instruction_labelframe = tk.LabelFrame(
            self.face_window,
            text="Instructions",
            font=("Segoe UI bold", 12),
            background="#f2f3f1",
            foreground="black"
        )
        self.instruction_labelframe.place(relx=0.707, rely=0.185, height=160, width=240)

        instruction_text = "Check User: Verify whether the user is registered.\nRegister New User: Create a new user.\nExit: Exit application."
        self.instruction_message = util.get_message(self.face_window, instruction_text, width=200, background="#f2f3f1", foreground="black")
        self.instruction_message.place(relx=0.728, rely=0.24, height=120, width=200)


    def add_webcam(self, label):
        """ Add webcam feed to the label.
        """

        if 'cap' not in self.__dict__:  # If self.cap is not defined
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()


    def process_webcam(self):
        """ Process webcam feed.
        """

        ret, frame = self.cap.read()

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        self.most_recent_capture_arr = frame
        img = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        # Repeat the same process each 20 ms
        self._label.after(20, self.process_webcam)

    def check_user(self):
        label = test(
            image=self.most_recent_capture_arr,
            model_dir=self.spoofing_model_dir,
            device_id=0
        )

        if label == 1:  # Real face
            name = util.recognize(self.most_recent_capture_arr, self.db_dir)

            if name in ["unknown_person", "no_persons_found"]:
                util.msg_box(
                    "Error!", "User not found! Please register new user or try again.", parent=self.face_window)

            else:
                util.msg_box("Success!", f"You've registered as {name}!", parent=self.face_window)
                logging.error(f"New user registered as {name}")

        else:
            util.msg_box("Error!", "Not a real face!", parent=self.face_window)

    
    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.face_window)
        self.register_new_user_window.configure(background="#f2f3f1")
        self.register_new_user_window.geometry(
            "960x540+430+180")  # Same size but moved a bit
        self.register_new_user_window.title("Register New User")

        # Buttons
        self.accept_button_register_new_user_window = util.get_button(
            self.register_new_user_window, "Accept", "#02a5a7", self.accept_register_new_user, fg="white")
        self.accept_button_register_new_user_window.place(relx=0.707, rely=0.71, height=50, width=240)

        self.try_again_button_register_new_user_window = util.get_button(
            self.register_new_user_window, "Try Again", "#f58a1d", self.try_again_register_new_user, fg="white")
        self.try_again_button_register_new_user_window.place(relx=0.707, rely=0.839, height=50, width=240)

        # Label
        self.frame_register_new_user_window = tk.Frame(self.register_new_user_window, background="#02a5a7")
        self.frame_register_new_user_window.place(relx=0.031, rely=0.074, height=463, width=604)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(relx=0.043, rely=0.092, height=442, width=581)

        self.add_img_to_label(self.capture_label)

        # Text
        self.text_label_register_new_user = util.get_text_label(
            self.register_new_user_window, "Enter your name:", "#f2f3f1")
        self.text_label_register_new_user.place(relx=0.707, rely=0.065, height=60, width=240)

        self.entry_text_register_new_user = util.get_entry_text(
            self.register_new_user_window)
        self.entry_text_register_new_user.place(relx=0.707, rely=0.185, height=160, width=240)


    def add_img_to_label(self, label):
        """ Add an image to the label.
        """

        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def accept_register_new_user(self):
        """ Process the registration of a new user.
            This function assumed that the user only created one face image.
        """
 
        new_name = self.entry_text_register_new_user.get(1.0, "end-1c")
        # 1.0 is the first character of the first line
        # end-1c is the last character of the last line (excluding the last character - a newline)

        if new_name == "":
            util.msg_box("Error!", "Please enter a name!", parent=self.register_new_user_window)
            self.register_new_user_window.destroy()

        label = test(
            image=self.register_new_user_capture,
            model_dir=self.spoofing_model_dir,
            device_id=0
        )

        if label == 1:  # Real face
            new_name = new_name.replace(" ", "_")
            name = util.recognize(self.register_new_user_capture, self.db_dir)

            if name == "unknown_person":
                embeddings = face_recognition.face_encodings(
                    self.register_new_user_capture)[0]

                img_path = os.path.join(self.db_dir, f'{new_name}.pickle')
                file = open(img_path, 'wb')
                pickle.dump(embeddings, file)

                util.msg_box("Success!", "User registered successfully!", parent=self.register_new_user_window)
                self.register_new_user_window.destroy()

            elif name == new_name:
                util.msg_box("Error!", "Username already exists!", parent=self.register_new_user_window)
                self.register_new_user_window.destroy()

            else:
                util.msg_box(
                    "Error!", "No persons found or Registered under a different username!", parent=self.register_new_user_window)
                self.register_new_user_window.destroy()

        else:
            util.msg_box("Error!", "Not a real face!", parent=self.register_new_user_window)
            self.register_new_user_window.destroy()

    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def exit(self):
        # Release resources
        if 'cap' in self.__dict__:
            self.cap.release()
        cv2.destroyAllWindows()
        self.main_window.destroy()

    def start(self):
        self.main_window.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
