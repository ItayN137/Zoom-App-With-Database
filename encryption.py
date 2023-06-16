import pickle

import rsa
from Crypto.Random import get_random_bytes
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def generate_rsa_keys():
    public_key, private_key = rsa.newkeys(1024)
    return public_key, private_key


def encrypt_rsa(data, public_key):
    return rsa.encrypt(data, public_key)


def decrypt_rsa(data, private_key):
    dectypted_data = rsa.decrypt(data, private_key)
    return dectypted_data


def create_AES_key_iv():
    key = get_random_bytes(16)
    iv = get_random_bytes(16)

    return key, iv


def generate_cipher(key, iv):
    return AES.new(key, AES.MODE_CBC, iv)


def encrypt_AES(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))


def decrypt_AES(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext


def encrypt_MD5(data):
    return hashlib.md5(data.encode()).hexdigest()
