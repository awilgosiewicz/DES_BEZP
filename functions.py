import re
from tables import *
import binascii
import itertools

def FileRead(filename):
    try:
        file = open(filename, 'rb')
        input = file.read()
        file.close()
        return input
    except IOError:
        print("Unreadable")


def FileWrite(string):
    try:
        file = open('output.txt', 'w')
        file.write(string)
        file.close()
        print("Saved")
    except IOError:
        print("Something went wrong here.")


# change input message from string to binary
def StringToBinary(string):
    # output = ''.join(format(ord(x), 'b') for x in string)
    output = ""
    for i in string:
        binary = bin(ord(i))[2:]
        for j in range(0, 8 - len(binary)):
            binary = '0' + binary
            output += binary
    return output


# change binary message to string
def BinaryToString(binstring):
    ##output = b'%d'.decode('utf-8') % binstring
    output = ""
    string = re.findall(r'.{8}', binstring)
    for i in string:
        output += chr(int(i, 2))
    return output


def BinaryToHex(binstring):
    output = ""
    string = re.findall(r'.{64}', binstring)
    for i in string:
        output += (hex(int(i, 2)) + '\n').upper()
    return output


def SliceString(string):
    slice = len(string)
    if slice % 64 != 0:
        for i in range(64 - (slice % 64)):
            string += '0'
    return string


def InitialPermutation(data):
    left = [0] * 32
    right = [0] * 32

    for i in range(0, 32):
        left[i] = data[IP_TABLE[i] - 1]
    for i in range(32, 64):
        right[i - 32] = data[IP_TABLE[i] - 1]
    return left, right


def FinalPermutation(left, right):
    merge = []
    output = [0] * 64

    for i in range(32):
        merge.append(left[i])
    for i in range(32):
        merge.append(right[i])

    for i in range(64):
        output[i] = merge[FP_TABLE[i] - 1]

    return output


def ExpansionFunction(data):
    output = [0] * 48
    for i in range(48):
        output[i] = data[E_TABLE[i] - 1]
    return output


def XOR_Function(data1, data2):
    output = []
    for i in range(0, len(data1)):
        output.append(data1[i] ^ data2[i])
    return output


def Permutation(string):
    output = [0] * 32
    for i in range(32):
        output[i] = string[P_TABLE[i] - 1]
    return output


def PermutedChoice1(key):
    output1 = [0] * 28
    for x in range(28):
        output1[x] = key[PC_1[x] - 1]
    output2 = [0] * 28
    for x in range(28, 56):
        output2[x - 28] = key[PC_1[x] - 1]
    return output1, output2


def PermutedChoice2(key):
    output = [0] * 48
    for x in range(48):
        output[x] = key[PC_2[x] - 1]
    return output


# 6 bits on input and #bits on output
def SBOXFunction(data):
    output = []
    for x in range(8):
        element = [0] * 6
        for j in range(6):
            element[j] = data[x * 6 + j]
        row = element[0] * 2 + element[5]
        col = element[1] * 8 + element[2] * 4 + element[3] * 2 + element[4]
        for j in range(3, -1, -1):
            output.append((S_BOX[x][row][col] >> j) & 1)
    return output


def FFunction(data, key):
    # expanding to 48 bits
    expanded = ExpansionFunction(data)
    # XOR
    xored = XOR_Function(expanded, key)
    # S-box substitution
    substituted = SBOXFunction(xored)
    # Permutation
    permuted = Permutation(substituted)
    output = permuted
    return output


def KeySchedule(array, round_num):
    key_array = [0] * 28
    # In rounds i=1,2,9,16 two halves are each rotated by one bit left and in all other 2 bits left (taken from SHIFT array)
    num_shift = SHIFT[round_num]
    return array[num_shift:] + array[:num_shift]


def KeyMerge(leftK, rightK):
    half_output = []
    merge_output = [0] * 48
    for i in range(28):
        half_output.append(leftK[i])
    for i in range(28):
        half_output.append(rightK[i])
    for i in range(48):
        merge_output[i] = half_output[PC_2[i] - 1]
    return merge_output


def SliceKey(key):
    output = len(key)
    if output < 64:
        if output % 64 != 0:
            for i in range(64 - (output % 64)):
                key += '0'
    return key


def Encryption(LData, RData, Lkey, Rkey):
    temp_Lkey = Lkey
    temp_Rkey = Rkey
    temp_LData = LData
    temp_RData = RData
    for i in range(16):
        temp_Rkey = KeySchedule(temp_Rkey, i)
        temp_Lkey = KeySchedule(temp_Lkey, i)
        mergedkey = KeyMerge(temp_Lkey, temp_Rkey)
        Ffunction_out = FFunction(temp_RData, mergedkey)
        temp_ = temp_LData
        temp_LData = temp_RData
        temp_RData = XOR_Function(Ffunction_out, temp_)
    return temp_LData, temp_RData


def display(array):
    for i in range(0, len(array), 4):
        hex_num = array[i] * 8 + array[i+1] * 4 + array[i+2] * 2 + array[i+3] * 1
        print(format(hex_num, 'X'), end='')
        if(i % 64 == 60):
            print("\n")
    print("")

def FinalFunction(input, key):
    data_array = []
    keys_array = []
    coded = []
    # reading byte bit by bit
    for element in input:
        for bit_ in range(7, -1, -1):
            data_array.append(element >> bit_ & 1)

    # slicing to 64 bits and padding with 0s if the number of bits is lower
    if len(data_array) % 64:
        for i in range(64 - (len(data_array) % 64)):
            data_array.append(0)

    # reading byte bit by bit
    for element in range(len(data_array)):
        for bitkey in range(7, -1, -1):
            keys_array.append(key[element] >> bitkey & 1)

    for element in range(0, len(data_array), 64):
        LeftHalf, RightHalf = InitialPermutation(data_array[element:element + 64])
        LeftKey, RightKey = PermutedChoice1(keys_array[element:element + 64])
        LeftHalf, RightHalf = Encryption(LeftHalf, RightHalf, LeftKey, RightKey)
        Output = FinalPermutation(LeftHalf, RightHalf)

        coded.append(Output)

    flatList = list(itertools.chain(*coded))

    print("Text to encode: \n")
    display(data_array)
    print("Key to encode: \n")
    display(keys_array)
    print("DES output: \n")
    display(flatList)

    listToString = ''.join([str(elem) for elem in flatList])
    hexList = BinaryToHex(listToString)
    FileWrite(hexList)
