# https://stackoverflow.com/questions/49511753/python-byte-image-to-numpy-array-using-opencv
import cv2
import numpy as np

# f = open('image.jpg', 'rb')
# image_bytes = f.read()  # b'\xff\xd8\xff\xe0\x00\x10...'

# decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)

# # print('OpenCV:\n', decoded)
# print('OpenCV:\n', decoded.shape)

# # your Pillow code
# import io
# from PIL import Image
# image = np.array(Image.open(io.BytesIO(image_bytes))) 
# # print('PIL:\n', image)





f = open('image.jpg', 'rb')
image_bytes = f.read()  # b'\xff\xd8\xff\xe0\x00\x10...'

decoded = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
#to bytes then back (this is my problem right here)
#https://stackoverflow.com/questions/53376786/convert-byte-array-back-to-numpy-array
decodedbytes = decoded.tobytes()
# decoded2 = cv2.imdecode(np.frombuffer(decoded, np.uint8), -1)
#reference: my own suffering:
decoded2 = np.frombuffer(decodedbytes, np.uint8).copy().reshape(91, 84, 3) #copy because frombuffer is immutable, reshape because it's wrong size


# print('OpenCV:\n', decoded)
print('OpenCV:\n', decoded2.shape, decoded2 == decoded)
