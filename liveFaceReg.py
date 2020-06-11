import faceReg
import cv2

names, encoding = faceReg.load_encoding()
faceReg.display(encoding, names)
cv2.destroyAllWindows()
