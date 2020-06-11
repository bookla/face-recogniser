import pickle
from os import listdir
from os.path import join, isfile
import time
import csv
import face_recognition


def compile():
    print("Encoding Known Faces...")
    quality = int(input("Encoding Quality : "))
    timer = time.time()
    # Look for folders
    face_files = [f for f in listdir(r"C:\Users\Book\Desktop\face recogniser\faces") if isfile(join(r"C:\Users\Book\Desktop\face recogniser\faces", f))]
    face_map = {}
    with open(r'C:\Users\Book\Desktop\face recogniser\map.csv') as csv_file:
        face_map = dict(filter(None, csv.reader(csv_file)))
    face_encoding = []
    face_names = []
    total = len(face_files)
    counter = 0
    for each_file in face_files:
        file_name = each_file[:each_file.index(".")]
        if face_map[file_name] != "Unknown":
            known_image = face_recognition.load_image_file(join(r"C:\Users\Book\Desktop\face recogniser\faces", each_file))
            known_face_encodings = face_recognition.face_encodings(known_image, num_jitters=quality)
            if len(known_face_encodings) != 0:
                known_face_encoding = known_face_encodings[0]
                # Get the actual name of the person then append it to the list
                face_names.append(face_map[file_name])
                # Load the file, encode it then add to the face encoding
                face_encoding.append(known_face_encoding)
                counter += 1
        if time.time() - timer > 1:
            print("Encoding Faces... " + str(counter/total*100) + "% Completed")
            timer = time.time()
    with open(r"C:\Users\Book\Desktop\face recogniser\face_encoding.pkl", 'wb') as f:
        pickle.dump([face_names, face_encoding], f)
    print("Compiled Successfully")
