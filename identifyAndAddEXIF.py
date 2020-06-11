from faceReg import match, load_encoding
import face_recognition
import cv2
from pyexiv2 import Image
from os.path import join, isfile
from os import listdir
import operator
import csv
from shutil import copyfile
from math import fabs


def identify():
    names, encoding = load_encoding()
    input_images = [f for f in listdir(r"C:\Users\Book\Desktop\face recogniser\input_image") if isfile(join(r"C:\Users\Book\Desktop\face recogniser\input_image", f))]
    total = len(input_images)
    counter = 1
    name_data = {}
    unknown_faces = {}
    for each_image in input_images:
        print("Identifying " + str(counter) + "/" + str(total))
        print(each_image)
        counter += 1
        current_image = cv2.imread(join(r"C:\Users\Book\Desktop\face recogniser\input_image", each_image))
        face_locations = face_recognition.face_locations(current_image)
        face_id = -1
        print(str(len(face_locations)) + " faces detected in this image")
        known = 0
        if len(face_locations) != 0:
            faces_data = match(current_image, face_locations, encoding, names, encoding_quality=5)
            for each_face in faces_data:
                face_id += 1
                sorted_face_distance = sorted(each_face.items(), key=operator.itemgetter(1))
                name = sorted_face_distance[0][0]
                distance = sorted_face_distance[0][1]
                second_distance = sorted_face_distance[1][1]
                if distance < 0.40 and fabs(second_distance - distance) > 0.1:
                    if each_image in name_data.keys():
                        name_data[each_image].append(name)
                    else:
                        name_data[each_image] = [name]
                    known += 1
                else:
                    top, right, bottom, left = face_locations[face_id]
                    crop_img = current_image[top:bottom, left:right]
                    unknown_data = [name, crop_img]
                    if each_image not in unknown_faces.keys():
                        unknown_faces[each_image] = [unknown_data]
                    else:
                        unknown_faces[each_image].append(unknown_data)
                    if each_image not in name_data.keys():
                        name_data[each_image] = []
        else:
            name_data[each_image] = []
        print("Able to confidently identify " + str(known) + "/" + str(len(face_locations)) + " faces \n")
    return name_data, unknown_faces


def save_face(cropped_image, for_name):
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        current_data = dict(filter(None, csv.reader(csv_file)))
        csv_file.close()
    int_values = [int(f.replace(".jpg", "").replace("face", "")) for f in current_data.keys() if f != ""]
    current_files = sorted(int_values)
    max_index = current_files[len(current_files) - 1]
    available_values = sorted([e for e in range(max_index) if e not in int_values])
    available_values.append(max_index + 1)
    new_name = "face" + str(available_values[0]) + ".jpg"
    cv2.imwrite(join(r'C:\Users\Book\Desktop\face recogniser\faces', new_name), cropped_image)
    current_data[new_name.replace(".jpg", "")] = for_name
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv', "w") as csv_write:
        w = csv.writer(csv_write)
        w.writerows(current_data.items())
        csv_write.close()


def resolve_unknowns(known, unknown):
    new_known = known
    for file_name, data_set in unknown.items():
        for data in data_set:
            predicted_name = data[0]
            image = data[1]
            cv2.imshow(file_name, image)
            print("Is this " + predicted_name + "?")
            key = cv2.waitKey(0)
            if key == ord("y") or key == ord("Y"):
                actual_name = predicted_name
            elif key == ord("n") or key == ord("N"):
                actual_name = input("Who is this person?")
            else:
                if key == ord("d") or key == ord("D"):
                    print("Discarding...")
                else:
                    print("Unknown Option Error")
                cv2.destroyAllWindows()
                continue
            if "y" in input("Use image as sample?").lower():
                save_face(image, actual_name)
            if file_name in new_known.keys():
                new_known[file_name].append(actual_name)
            else:
                new_known[file_name] = [actual_name]
            cv2.destroyAllWindows()
    return new_known


def add_to_exif(known):
    for file_name, identified_names in known.items():
        name_string = ""
        for each_name in identified_names:
            if name_string == "":
                name_string = each_name
            else:
                name_string += ", " + each_name
        copyfile(join(r"C:\Users\Book\Desktop\face recogniser\input_image", file_name), join(r"C:\Users\Book\Desktop\face recogniser\tagged_image", file_name))
        i = Image(join(r"C:\Users\Book\Desktop\face recogniser\tagged_image", file_name))
        i.modify_exif({"Exif.Image.Make": name_string})

def start():
    known, unknowns = identify()
    known = resolve_unknowns(known, unknowns)
    print("Saving Files")
    add_to_exif(known)


start()