import pickle

with open('face_encoding.pkl', 'rb') as f:  # Python 3: open(..., 'rb')
    names, encodings = pickle.load(f)

print(names, encodings)