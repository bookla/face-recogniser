import pickle
import collections

with open('face_encoding.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
    names, encodings = pickle.load(f)

new_names = []
for each_name in names:
    if each_name not in new_names:
        new_names.append(each_name)

print("Able to recognise " + str(len(new_names)) + " faces with >60% confidence")
print("After analysing " + str(len(names)) + " samples of faces")
print("\nNames which can be identified includes: ")
[print(sorted(new_names)[n], "        ", sorted(new_names)[n+1]) for n in range(len(new_names) - 1) if n%2 == 0]

face_count = {}
for each_name in names:
    if each_name not in face_count.keys():
        face_count[each_name] = 1
    else:
        face_count[each_name] += 1
print("\n\n\n\nSorted By : Number of Samples")
sorted_x = sorted(face_count.items(), key=lambda kv: kv[1])
sorted_x.reverse()
[print(str(i + 1), ": ", sorted_x[i][0], " "*(20 - len(sorted_x[i][0])), sorted_x[i][1]) for i in range(len(sorted_x) - 1)]
