from functions import *


input_file = open("input.txt", "rb")
key_file = open("randomBig.bin", "rb")
input = input_file.read()
key = key_file.read()

FinalFunction(input, key)


