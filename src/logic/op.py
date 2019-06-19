import numpy as np
import cv2
import scipy.spatial.distance as ssd

def encode(path,msg,length):
    print("[src.logic.op.encode]")

    img = cv2.imread(path,1)

    print("Image Path : " + path)

    rows, columns, channels = np.shape(img)
    i_r = 0
    i_c = 0
    i_ch = 0
    for i in range(8):
        num = ord('*')
        for j in range(8):
            code = num %2
            num = int(num /2)
            if code == 1:
                img[i_r ,i_c ,i_ch] += 1 - img[i_r ,i_c ,i_ch ] %2
            else:
                img[i_r ,i_c ,i_ch] += img[i_r ,i_c ,i_ch ] %2
            i_r += 1
            if i_r >= rows :
                i_r = 0
                i_c += 1
            if i_c >= columns:
                i_c = 0
                i_ch += 1

    for j in range(16):
        code = length % 2
        length = int(length / 2)
        if code == 1:
            img[i_r, i_c, i_ch] += 1 - img[i_r, i_c, i_ch] % 2
        else:
            img[i_r, i_c, i_ch] += img[i_r, i_c, i_ch] % 2
        i_r += 1
        if i_r >= rows:
            i_r = 0
            i_c += 1
        if i_c >= columns:
            i_c = 0
            i_ch += 1

    for i in msg:
        num = ord(i)
        for j in range(8):
            code = num %2
            num = int(num /2)
            if code == 1:
                img[i_r ,i_c ,i_ch] += 1 - img[i_r ,i_c ,i_ch ] %2
            else:
                img[i_r ,i_c ,i_ch] += img[i_r ,i_c ,i_ch ] %2
            i_r += 1
            if i_r >= rows :
                i_r = 0
                i_c += 1
            if i_c >= columns:
                i_c = 0
                i_ch += 1
    decode1(img)
    cv2.imwrite(path, img)


def decode1(img):
    rows, columns, channels = np.shape(img)
    i_r = 0
    i_c = 0
    i_ch = 0
    text = ''
    for i in range(20):
        num = 0
        for j in range(8):
            num += (img[i_r, i_c, i_ch] % 2) * (2 ** j)
            i_r += 1
            if i_r >= rows:
                i_r = 0
                i_c += 1
            if i_c >= columns:
                i_c = 0
                i_ch += 1
        text += chr(num)
    print("Decoded Text : " + text)

def decode(path):
    print("[src.logic.op.decode]")
    print(path)
    img = cv2.imread(path, 1)

    print("Image Path : " + path)
    text = ""
    rows, columns, channels = np.shape(img)
    print("HWLLLL")
    i_r = 0
    i_c = 0
    i_ch = 0
    max_char = int((rows * columns * channels) / 8)

    for i in range(8):
        num = 0
        for j in range(8):
            num += (img[i_r, i_c, i_ch] % 2) * (2 ** j)
            i_r += 1
            if i_r >= rows:
                i_r = 0
                i_c += 1
            if i_c >= columns:
                i_c = 0
                i_ch += 1
        text += chr(num)
    if text != '********':
        return (False, '')
    num = 0
    for j in range(16):
        num += (img[i_r, i_c, i_ch] % 2) * (2 ** j)
        i_r += 1
        if i_r >= rows:
            i_r = 0
            i_c += 1
        if i_c >= columns:
            i_c = 0
            i_ch += 1
    length = num
    print(length)
    text = ''
    for i in range(length):
        num = 0
        for j in range(8):
            num += (img[i_r, i_c, i_ch] % 2) * (2 ** j)
            i_r += 1
            if i_r >= rows:
                i_r = 0
                i_c += 1
            if i_c >= columns:
                i_c = 0
                i_ch += 1
        text += chr(num)
    return (True,text)

def dHash(path):
    print("[src.logic.op.dHash]")

    img = cv2.imread(path, 1)
    resized_img = cv2.resize(img, dsize=(9,9), interpolation=cv2.INTER_NEAREST)
    gray_image = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    img_d_col = np.diff(gray_image)
    img_d_row = np.diff(np.transpose(gray_image))
    img_flatten = np.vstack((img_d_col, img_d_row)).flatten()
    img_hash = np.array(img_flatten > 0, dtype='int')
    return img_hash

def hamming_distance(hash1,hash2):
    print("[src.logic.op.hamming_distance]")
    print("Hash1 Shape : " + str(np.shape(hash1)))
    print("Hash2 Shape : " + str(np.shape(hash2)))
    return ssd.hamming(hash1, hash2)