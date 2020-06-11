import face_recognition
from os.path import join, isfile
from os import listdir
import cv2
import csv
import time

vc = cv2.VideoCapture(0)

def save_unknown(snapshot, face_location):
    top, right, bottom, left = face_location
    crop_img = snapshot[top:bottom, left:right]
    # crop_img = snapshot[new_top:new_bottom, new_left:new_right]
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        current_data = dict(filter(None, csv.reader(csv_file)))
        csv_file.close()
    int_values = [int(f.replace(".jpg", "").replace("face", "")) for f in current_data.keys() if f != ""]
    current_files = sorted(int_values)
    max_index = current_files[len(current_files) - 1]
    available_values = sorted([e for e in range(max_index) if e not in int_values])
    available_values.append(max_index + 1)
    new_name = "face" + str(available_values[0]) + ".jpg"
    cv2.imwrite(join(r'C:\Users\Book\Desktop\face recogniser\faces', new_name), crop_img)
    current_data[new_name.replace(".jpg", "")] = "Unknown"
    print(current_data)
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv', "w") as csv_write:
        w = csv.writer(csv_write)
        w.writerows(current_data.items())
        csv_write.close()


images = face_files = [f for f in listdir(r"C:\Users\Book\Desktop\face recogniser\images") if isfile(join(r"C:\Users\Book\Desktop\face recogniser\images", f))]
print(images)
cv2.namedWindow("Preview", cv2.WND_PROP_FULLSCREEN)
for image_file in images:
    each_image = cv2.imread(join(r"C:\Users\Book\Desktop\face recogniser\images", image_file))
    print("Image Loaded, Identifying Faces")
    face_locations = face_recognition.face_locations(each_image)
    image_with_box = each_image
    for each_face in face_locations:
        print(each_face)
        save_unknown(each_image, each_face)
        top, right, bottom, left = each_face
        image_with_box = cv2.rectangle(each_image, (left, top), (right, bottom), (255, 0, 0), 15)
    cv2.imshow("Preview", image_with_box)
    cv2.waitKey(100)
print("Import Complete Learning Will Start")
from learn import main as start_learn
start_learn()
