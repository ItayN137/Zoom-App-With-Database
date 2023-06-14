import rsa
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import hashlib
from Crypto.Cipher import AES
from  Crypto.Util.Padding import pad, unpad

def generate_rsa_keys(client_socket):
    public_key, private_key = rsa.newkeys(1024)

    with open("public.pem", "wb") as f:
        f.write(public_key.save_pkcs1("PEM"))

    with open("private.pem", "wb") as f:
        f.write(private_key.save_pkcs1("PEM"))

    client_socket.send(public_key)
    return public_key, private_key


def encrypt_rsa(data, public_key):
    return rsa.encrypt(data.encode(), public_key)


def decrypt_rsa(data, private_key):
    dectypted_data = rsa.decrypt(data, private_key)
    return dectypted_data.decode()


def create_AES_key():
    salt = get_random_bytes(32)
    password = "ldolwDDw129d"

    key = PBKDF2(password, salt, dkLen=32)

    cipher = AES.new(key, AES.MODE_CBC)
    return cipher


def encrypt_AES(data, cipher):
    ciphered_data = cipher.encrypt(pad(data, AES.block_size))


def decrypt_AES(data, cipher):
    decrypted_data = unpad(cipher.dectypt(data), AES.block_size)


def encrypt_MD5(data):
    return hashlib.md5(data).hexdigest()




