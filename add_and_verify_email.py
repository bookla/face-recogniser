import csv
import pickle

with open('face_encoding.pkl', 'rb') as enc:  # Python 3: open(..., 'rb')
    names, encodings = pickle.load(enc)
new_names = []
for each_name in names:
    if each_name not in new_names:
        new_names.append(each_name)
with open('email.csv', 'r') as email:
    email_data = dict(filter(None, csv.reader(email)))
    email.close()
email_not_exist = []
for each_name in new_names:
    if each_name not in email_data.keys():
        email_not_exist.append(each_name)
new_email_data = email_data
for each_new_name in email_not_exist:
    print("New name detected : " + each_new_name + ". Adding...")
    new_email_data[each_new_name] = "None"
email_missing = []
for name, email in new_email_data.items():
    if email == "None":
        email_missing.append(name)
for each_missing_email in email_missing:
    print("Email Field Empty For: " + each_missing_email)
print(str(len(email_missing)) + " email fields missing...")
with open(r'email.csv', "w") as csv_write:
    w = csv.writer(csv_write)
    w.writerows(new_email_data.items())
    csv_write.close()
