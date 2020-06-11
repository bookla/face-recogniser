import face_recognition
import cv2
from os.path import join
import csv
import operator
import numpy
import pickle


vc = cv2.VideoCapture(0)
print("Initialising...")


def save_unknown(snapshot, face_location):
    top, right, bottom, left = face_location
    width, height, ch = snapshot.shape
    new_top = top - 30
    if new_top < 0:
        new_top = 0
    new_left = left - 30
    if new_left < 0:
        new_left = 0
    new_right = right + 30
    if new_right > width:
        new_right = width
    new_bottom = bottom + 30
    if new_bottom > height:
        new_bottom = height
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


def scale_face_location(original_locations, scale , width, height):
    face_locations = []
    for each_face in original_locations:
        top, right, bottom, left = each_face
        new_top = top * scale - 10
        new_right = right * scale + 10
        new_bottom = bottom * scale + 10
        new_left = left * scale - 10
        if new_top < 0:
            new_top = 0
        if new_right >= width:
            new_right = width - 1
        if new_left < 0:
            new_left = 0
        if new_bottom >= height:
            new_bottom = height - 1
        face_locations.append((int(new_top), int(new_right), int(new_bottom), int(new_left)))
    return face_locations


def display(known_encoding, known_names):
    global brightness
    if "y" in input("Full HD Mode?").lower():
        vc.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    total_face = 0
    face_identified = 0
    face_unsure = 0
    new_faces = 0
    frame_num = 0
    interval = 3
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    # print(known_encoding, known_names)
    if rval:
        print("Camera Initialisation Complete")
        print(frame.shape)
    matches = []
    cv2.namedWindow("Live Recognition", cv2.WND_PROP_FULLSCREEN)
    while rval:
        height, width, channels = frame.shape
        scaled_down_frame = cv2.resize(frame, (720, 405))
        scale = width/720
        frame_with_box = frame
        if frame_num % interval == 0:
            scaled_face_locations = face_recognition.face_locations(scaled_down_frame)
            face_locations = scale_face_location(scaled_face_locations, scale, width, height)
            # If face found compute matches
            if len(face_locations) > 0:
                match_frame = cv2.resize(frame, (1280, 720))
                match_locations = scale_face_location(face_locations, 0.66666, width, height)
                matches = match(match_frame, match_locations, known_encoding, known_names)
                count = 1
                for each_face_match in matches:
                    total_face += 1
                    sorted_face_match = sorted(each_face_match.items(), key=operator.itemgetter(1))
                    distance = sorted_face_match[0][1]
                    if distance > 0.5 and frame_num % (interval * 1) == 0:
                        save_unknown(frame, face_locations[count - 1])
                    count += 1
            else:
                print("No face detected\n")
        count = 1

        face_count_text = "Found " + str(len(face_locations)) + " face(s) in frame"
        cv2.putText(frame_with_box, face_count_text, (250, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        total_face_text = "Found " + str(total_face) + " faces this session"
        identified_text = "Identified " + str(face_identified) + " faces this session"
        unsure_text = "Unsure about " + str(face_unsure) + " faces this session"
        new_faces_text = str(new_faces) + " new faces waiting to be identified"
        cv2.putText(frame_with_box, total_face_text, (250, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame_with_box, identified_text, (1000, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame_with_box, unsure_text, (800, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(frame_with_box, new_faces_text, (800, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Draw Rectangles ETC
        if len(face_locations) >= len(matches):
            for each_face_match in matches:
                if "Unknown" in each_face_match.keys():
                    del each_face_match["Unknown"]
                print("Face " + str(count))
                sorted_face_match = sorted(each_face_match.items(), key=operator.itemgetter(1))
                most_likely_name = sorted_face_match[0][0]
                distance = sorted_face_match[0][1]
                text_location = (face_locations[count - 1][3], face_locations[count - 1][0] - 10)
                if face_locations[count - 1][1] - face_locations[count - 1][3] < 110:
                    frame_with_box = cv2.putText(frame_with_box, "Move Closer!", text_location, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
                    print("Face too far\n")
                elif distance <= 0.40:
                    frame_with_box = cv2.putText(frame_with_box, most_likely_name + " " + str(percentage_match(distance)) + "%", text_location, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                    print(most_likely_name, distance)
                    print("")
                    if frame_num % interval == 0:
                        face_identified += 1
                elif distance <= 0.5:
                    if frame_num % interval == 0:
                        face_unsure += 1
                    frame_with_box = cv2.putText(frame_with_box, "(" + most_likely_name + ")? " + str(percentage_match(distance)) + "%", text_location, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 137, 255), 3)
                    print("Unknown with likely candidates (" + most_likely_name + ") " + str(distance) + "\n")
                else:
                    frame_with_box = cv2.putText(frame_with_box, "Unknown", text_location, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                    print("Unknown " + str(distance) + "\n")
                    new_faces += 1
                count += 1
        for each_rec in face_locations:
            top, right, bottom, left = each_rec
            frame_with_box = cv2.rectangle(frame_with_box, (left, top), (right, bottom), (255, 0, 0), 3)


        cv2.imshow("Live Recognition", frame_with_box)
        rval, frame = vc.read()
        key = cv2.waitKey(5)
        frame_num += 1
        if key == 27:
            break


def load_encoding():
    with open(r'C:\Users\Book\Desktop\face recogniser\face_encoding.pkl', 'rb') as f:
        face_names, face_encoding = pickle.load(f)
        return face_names, face_encoding


def percentage_match(distance):
    power = 2
    max_val = 0.7**power
    min_val = 0.25**power
    corrected_distance = distance**power
    adjusted_distance = corrected_distance - min_val
    percentage = 1 - (adjusted_distance/(max_val - min_val))
    return round(percentage*10000)/100


def match(unknown_image, locations, known_encoding, known_names, encoding_quality=1):
    # Encode the unknown image
    unknown_encodings = face_recognition.face_encodings(unknown_image, locations, encoding_quality)
    if len(unknown_encodings) == 0:
        return
    counter = 0
    matches_list = {}
    # Loop through encoding and find matches
    for each_encoding in known_encoding:
        corresponding_name = known_names[counter]
        matches = face_recognition.face_distance(unknown_encodings, numpy.array(each_encoding))
        if corresponding_name in matches_list.keys():
            matches_list[corresponding_name].append(matches)
            # adjusted_matches = []
            # count = 0
            # for each_face in matches:
            #    avg = (matches_list[corresponding_name][count] + each_face) / 2
            #    adjusted_matches.append(avg)
            #    count += 1
            # matches_probability[corresponding_name] = adjusted_matches
        elif corresponding_name not in matches_list.keys():
            matches_list[corresponding_name] = [matches]
            # matches_count[corresponding_name] = 1
        counter += 1
    data = []
    for each_face in range(len(locations)):
        matches_probability = {}
        for name, each_match_list in matches_list.items():
            # print(each_match_list)
            current_face = [i[each_face] for i in each_match_list]
            current_match_list = sorted(current_face)
            current_match_list.reverse()
            for each_value in current_match_list:
                if name not in matches_probability:
                    matches_probability[name] = each_value
                else:
                    matches_probability[name] = (matches_probability[name] + each_value)/2
        data.append(matches_probability)
    #number_of_faces = len(locations)
    #for each_face in range(number_of_faces):
    #    dictionary = {}
    #    for each_person, distance in matches_probability.items():
    #        dictionary[each_person] = distance[each_face]
    #    data.append(dictionary)
    return data


