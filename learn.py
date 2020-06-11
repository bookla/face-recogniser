import csv
import cv2
import face_recognition
from os.path import join, isfile
from os import listdir, remove
import operator
import time
import face_compiler
from faceReg import match


encoding_cache = {}

def encode_known():
    # Look for folders
    timer = time.time()
    face_files = [f for f in listdir(r"C:\Users\Book\Desktop\face recogniser\faces") if isfile(join(r"C:\Users\Book\Desktop\face recogniser\faces", f))]
    face_map = {}
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        face_map = dict(filter(None, csv.reader(csv_file)))
    face_encoding = []
    face_names = []
    total = len(face_files)
    counter = len(encoding_cache)
    if len(encoding_cache.keys()) == 0:
        print("Encoding Faces")
    for each_file in face_files:
        file_name = each_file[:each_file.index(".")]
        if file_name not in encoding_cache.keys():
            if len(encoding_cache.keys()) != 0:
                print("Encoding New Faces")
            known_image = face_recognition.load_image_file(
                join(r"C:\Users\Book\Desktop\face recogniser\faces", each_file))
            known_face_encodings = face_recognition.face_encodings(known_image)
            counter += 1
            if len(known_face_encodings) != 0:
                known_face_encoding = known_face_encodings[0]
                face_names.append(face_map[file_name])
                face_encoding.append(known_face_encoding)
                # Save Cache
                encoding_cache[file_name] = known_face_encoding
            else:
                print("Face Cannot Be Identified!")
                remove_item(file_name)
                return face_names, face_encoding, True
            if time.time() - timer > 1:
                print("Encoding Faces... " + str(counter/total*100) + "% Completed")
                timer = time.time()
        else:
            print("Using Cache For " + file_name)
            known_face_encoding = encoding_cache[file_name]
            face_names.append(face_map[file_name])
            face_encoding.append(known_face_encoding)
    return face_names, face_encoding, False


def get_most_likely(unknown_image):
    # Update Encoding
    names, encoding, err = encode_known()
    if err:
        return None, True
    if unknown_image is None:
        return None, True
    height, width, channels = unknown_image.shape
    matches = match(unknown_image, [(0, width, height, 0)], encoding, names)
    # We only care about the first face it sees
    matched = matches[0]
    # Remove unknowns
    del matched["Unknown"]
    sorted_names = sorted(matched.items(), key=operator.itemgetter(1))
    most_likely_name = sorted_names[0][0]
    distance = sorted_names[0][1]
    if distance < 0.36:
        skip = True
    else:
        skip = False
    return most_likely_name, skip


def save_name(face_file, name):
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        current_data = dict(filter(None, csv.reader(csv_file)))
        csv_file.close()
    current_data[face_file] = name
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv', "w") as csv_write:
        w = csv.writer(csv_write)
        w.writerows(current_data.items())
        csv_write.close()


def remove_item(face_file):
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        current_data = dict(filter(None, csv.reader(csv_file)))
        csv_file.close()
    del current_data[face_file]
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv', "w") as csv_write:
        w = csv.writer(csv_write)
        w.writerows(current_data.items())
        csv_write.close()
    print("Removed from csv")
    remove(join(r'C:\Users\Book\Desktop\face recogniser\faces', face_file + ".jpg"))
    print("Removed face file")
    if face_file in encoding_cache.keys():
        del encoding_cache[face_file]
    print("Removed from cache")


def main():
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        current_data = dict(filter(None, csv.reader(csv_file)))
        csv_file.close()
    loop_ran = 0
    for each_file, corresponding_name in current_data.items():
        print("\n" * 3)
        if corresponding_name == "Unknown":
            file_name = each_file + ".jpg"
            print("Loading and Identifying Person In " + file_name + "...")
            file_path = join(r'C:\Users\Book\Desktop\face recogniser\faces', file_name)
            image = cv2.imread(file_path)
            name, skip = get_most_likely(image)
            if not skip:
                cv2.imshow("Face Learner", image)
                print("Is this " + name + "?")
                key = cv2.waitKey(0)
                if key == ord("y"):
                    save_name(file_name.replace(".jpg", ""), name)
                    print("Saving " + file_name + " as " + name)
                elif key == ord("d"):
                    print("Discarding " + file_name)
                    remove_item(file_name.replace(".jpg", ""))
                else:
                    print("Who is this person?")
                    name = input()
                    save_name(file_name.replace(".jpg", ""), name)
                    print("Saving " + file_name + " as " + name)
            else:
                if name is None:
                    print("Skipping " + file_name + " image too small")
                else:
                    print("Discarding " + file_name + " person in the picture identified as " + name + " (Image Redundant)")
                    remove_item(file_name.replace(".jpg", ""))
            cv2.destroyAllWindows()
            loop_ran += 1
    return loop_ran


looping = True
while looping:
    i = main()
    if i != 0:
        print("Optimising")
    else:
        print("Optimised")
        looping = False
print("\n\nLearning Complete! (No More Unidentified Faces)")

print("Pre-compile Now?")
if "y" in input().lower():
    face_compiler.compile()