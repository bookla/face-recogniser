import cv2
from faceReg import load_encoding, match, scale_face_location
from os import listdir
from os.path import isfile, join
import face_recognition
import win32con
import win32api
import win32gui
import pygame
import numpy
import textwrap
import time
import operator
from math import fabs
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email import encoders
import csv

pygame.init()

display_width = 1920
display_height = 1080

mainDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Automated Camera Controller")

black = (0, 0, 0)
white = (255, 255, 255)

clock = pygame.time.Clock()
crashed = False


def face_found(in_image):
    return len(face_recognition.face_locations(in_image)) != 0


def waiting_screen(capture_device):
    if capture_device.isOpened():
        available, frame = capture_device.read()
    else:
        return
    mainDisplay.fill(white)
    while not face_found(frame):
        pygame.event.get()
        draw_text(mainDisplay, "Welcome!", (int(display_width / 2), int(display_height / 2)), size=200)
        pygame.display.update()
        available, frame = capture_device.read()
        clock.tick(30)
    wait_trigger(capture_device)


def draw_text(screen, text, center, colour=black, font=None, size=85, aa=True):
    font = pygame.font.Font(font, size)
    text = font.render(text, aa, colour)
    text_rect = text.get_rect(center=center)
    screen.blit(text, text_rect)


def get_names(frame, face_locations):
    names, encoding = load_encoding()
    matches_data = match(unknown_image=frame, locations=face_locations, known_encoding=encoding, known_names=names, encoding_quality=5)
    if matches_data is None:
        return []
    names = []
    for each_face in matches_data:
        sorted_face_match = sorted(each_face.items(), key=operator.itemgetter(1))
        most_likely_name = sorted_face_match[0][0]
        distance = sorted_face_match[0][1]
        second_distance = sorted_face_match[1][1]
        if distance < 0.42 and fabs(second_distance - distance) > 0.04:
            names.append(most_likely_name)
        elif distance < 0.48:
            names.append(most_likely_name + "?")
        else:
            names.append("Unknown")
    return names


def frame_to_pygame(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = numpy.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    return frame


def clear_screen(screen):
    screen.fill(white)


def is_triggered():
    events = pygame.event.get()
    if pygame.joystick.get_count() != 0:
        joystick = pygame.joystick.Joystick(0)
        value = joystick.get_axis(1)
        if value < -0.8:
            return True
        return False
    else:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        return False



def wait_trigger(capture_device):
    pygame.joystick.init()
    triggered = False
    available, frame = capture_device.read()
    frame_count = 0
    face_timer = 0
    clear_screen(mainDisplay)
    if pygame.joystick.get_count() != 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    while not triggered:
        triggered = is_triggered()
        if frame_count % 10 == 0:
            face_locations = face_recognition.face_locations(frame)
            names = get_names(frame, face_locations)
            clear_screen(mainDisplay)
            draw_text(mainDisplay, "Good Evening", (int(display_width / 2), int(display_height / 2) - 100), size=150)
            draw_text(mainDisplay, "Press and hold the left pedal to begin", (int(display_width / 2), int(display_height - 100)), size=50)
            text = ""
            print(names)
            for each_name in names:
                if text == "":
                    text += each_name
                else:
                    text += ", " + each_name
            wrapped_text = textwrap.fill(text, width=display_width - 100)
            draw_text(mainDisplay, wrapped_text, (int(display_width / 2), int(display_height / 2) + 100), size=120)
            pygame.display.update()
            available, frame = capture_device.read()
        if len(face_locations) == 0:
            if face_timer == 0:
                face_timer = time.time()
            elif time.time() - face_timer > 4:
                waiting_screen(capture_device)
        else:
            face_timer = 0
        clock.tick(15)
    if triggered:
        capture(live_capture_device=capture_device)


def capture(live_capture_device):
    clear_screen(mainDisplay)
    draw_text(mainDisplay, "Ready?", (int(display_width/2), int(display_height)/2))
    pygame.display.update()
    clock.tick(30)
    capture2 = False
    start_time = time.time()
    time_total = 10
    while time.time() - start_time <= time_total:
        pygame.event.get()
        time_difference = time.time() - start_time
        display_time = (time_total - 1) - (time.time() - start_time)
        clear_screen(mainDisplay)
        if time_difference > 1 and display_time > 3:
            draw_text(mainDisplay, str(int(display_time)), (int(display_width / 2), int(display_height / 2)), size=300)
        if display_time <= 6:
            available, frame = live_capture_device.read()
            frame = cv2.resize(frame, (1920, 1080))
            pygame_frame = frame_to_pygame(frame)
            mainDisplay.blit(pygame_frame, (0, 0))
            if display_time > 0:
                draw_text(mainDisplay, str(int(display_time)), (int(display_width - 400), int(display_height - 200)), size=300)
        if display_time <= 0 and not capture2:
            sony_capture_command()
            capture2 = True
        pygame.display.update()
    captured(live_capture_device)


def captured(capture_device):
    clear_screen(mainDisplay)
    draw_text(mainDisplay, "Downloading Images....", (int(display_width / 2), int(display_height / 2)))
    pygame.display.update()
    time.sleep(5)
    images, image_names = load_image()
    for each_image in images:
        pygame.event.get()
        clear_screen(mainDisplay)
        each_image = cv2.resize(each_image, (1920, 1080))
        pygame_image = frame_to_pygame(each_image)
        mainDisplay.blit(pygame_image, (0, 0))
        pygame.display.update()
        clock.tick(1)
    clear_screen(mainDisplay)
    draw_text(mainDisplay, "Identifying Faces....", (int(display_width / 2), int(display_height / 2)))
    pygame.display.update()
    identified_names = identify_images(images)
    sure_names, unsure_names = categorise_names(identified_names)
    clear_screen(mainDisplay)
    pygame.event.get()
    draw_text(mainDisplay, "Sending To : ", (int(display_width / 2), int(display_height / 2) - 50), size=150)
    print("Hi")
    text = ""
    for each_name in sure_names:
        if each_name != "Unknown":
            if text == "":
                text += each_name
            else:
                text += ", " + each_name
    if text == "":
        text = "No One"
    wrapped_text = textwrap.fill(text, width=display_width - 100)
    draw_text(mainDisplay, wrapped_text, (int(display_width / 2), int(display_height / 2) + 100), size=120)
    draw_text(mainDisplay, "More names are awaiting confirmation", (int(display_width / 2), int(display_height - 120)), size=50)
    print("Hi2")
    pygame.display.update()
    send_email(sure_names, image_names[:2])
    save_unsure(unsure_names, image_names[:2])
    clock.tick(1)
    time.sleep(3)
    waiting_screen(capture_device)


def get_email(for_names):
    with open(r'C:\Users\Book\Desktop\face recogniser\email.csv') as email_file:
        email_data = dict(filter(None, csv.reader(email_file)))
        email_file.close()
    address = []
    for each_name in for_names:
        if each_name.replace("?", "") in email_data.keys():
            address.append(email_data[each_name.replace("?", "")])
    print(address)
    return address


def compose_and_send(to, images):
    try:
        if len(to) == 0:
            return
        from_addr = "EMAIL" # TODO: CHANGE CREDENTIALS
        password = "PASSWORD"
        text = ""
        for each_email in to:
            if text == "":
                text = each_email
            else:
                text += ", " + each_email
        to_addr = text
        smtp_server = "smtp.office365.com"

        # email object that has multiple part:
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = Header('Backdrop Images', 'utf-8').encode()

        msg_content = MIMEText("This email was automatically sent by the automated tagging system. If you\'re not in the image and you think this email was sent by mistake you may ignore it or report it by replying to this email. The image has been attached below, please scroll down to see them..\n\n\n", "plain", "utf-8")
        msg.attach(msg_content)

        for each_image in images[:4]:
            with open(join(r"C:\Users\Book\Desktop\face recogniser\sony images", each_image), 'rb') as f:
                mime = MIMEBase('image', 'jpg', filename='img1.jpg')
                mime.add_header('Content-Disposition', 'attachment', filename='img1.jpg')
                mime.add_header('X-Attachment-Id', '0')
                mime.add_header('Content-ID', '<0>')
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                msg.attach(mime)
                f.close()
        server = smtplib.SMTP(smtp_server, 587)
        server.ehlo()
        server.starttls()
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
    except:
        print("SOME ERROR TOO BAD CONTINUE WORKING")


def send_email(names, images):
    address = get_email(names)
    compose_and_send(address, images)


def save_unsure(sure_names, images):
    last_image = images[0]
    with open(r"C:\Users\Book\Desktop\face recogniser\unsure.csv", "r") as unsure_file:
        unsure_data = dict(filter(None, csv.reader(unsure_file)))
        unsure_file.close()
    names_str = ""
    for each_name in sure_names:
        if names_str == "":
            names_str = each_name
        else:
            names_str += ", " + each_name
    unsure_data[last_image] = names_str
    with open(r"C:\Users\Book\Desktop\face recogniser\unsure.csv", "w") as save_file:
        w = csv.writer(save_file)
        w.writerows(unsure_data.items())
        save_file.close()




def identify_images(images):
    clear_screen(mainDisplay)
    draw_text(mainDisplay, "Identifying Faces...",  (int(display_width / 2), int(display_height / 2)))
    names_in_images = []
    for each_image in images:
        scale_percent = 40
        width, height, channel = each_image.shape
        width_scaled = int(each_image.shape[1] * scale_percent / 100)
        height_scaled = int(each_image.shape[0] * scale_percent / 100)
        scaled_image = cv2.resize(each_image, (width_scaled, height_scaled))
        face_locations_scaled = face_recognition.face_locations(scaled_image)
        face_locations = scale_face_location(face_locations_scaled, 100/scale_percent, width, height)
        names = get_names(each_image, face_locations)
        names_in_images.append(names)
    return names_in_images


def categorise_names(names_in_images):
    print(names_in_images)
    unsure = []
    sure = []
    total_names = []
    for image in names_in_images:
        for name in image:
            total_names.append(name)
    unique_names = []
    for each_name in total_names:
        if each_name not in unique_names:
            unique_names.append(each_name)
    for each_name in unique_names:
        if total_names.count(each_name) >= len(names_in_images) - 1:
            sure.append(each_name)
        else:
            unsure.append(each_name)
    return sure, unsure


def load_image():
    path = r"C:\Users\Book\Desktop\face recogniser\sony images"
    file_list = [f for f in listdir(path) if isfile(join(path, f))]
    sorted_file = sorted(file_list)
    sorted_file.reverse()
    print(sorted_file)
    images = []
    for each_file in range(4):
        image = cv2.imread(join(r"C:\Users\Book\Desktop\face recogniser\sony images", sorted_file[each_file]))
        images.append(image)
    return images, sorted_file


rect = []


def get_remote_window(hwnd, extra):
    global rect
    if win32gui.GetWindowText(hwnd) == "Remote":
        rect.append((hwnd, win32gui.GetWindowRect(hwnd)))
        print(rect)


top_windows = []


def window_enumeration_handler(hwnd, special):
    global top_windows
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def bring_window_to_front(name):
    win32gui.EnumWindows(window_enumeration_handler, None)
    print(top_windows)
    print(rect)
    named_windows = [window for window in top_windows if window[1] == "Remote" and win32gui.GetWindowRect(window[0])[0] > 0]
    # win32gui.ShowWindow(named_windows[1][0], 5)
    win32gui.SetForegroundWindow(named_windows[0][0])


def sony_capture_command():
    win32gui.EnumWindows(get_remote_window, None)
    # win32gui.BringWindowToTop(title="Remote")
    bring_window_to_front("Remote")
    x = rect[0][1][0]
    y = rect[0][1][1]
    w = rect[0][1][2] - x
    shutter_x = int(x + w/2 - 20)
    shutter_y = int(y + 200)
    win32api.SetCursorPos((shutter_x, shutter_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, shutter_x, shutter_y, 0, 0)
    time.sleep(1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, shutter_x, shutter_y, 0, 0)


def main():
    capture_device = cv2.VideoCapture(0)
    capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    waiting_screen(capture_device)


main()