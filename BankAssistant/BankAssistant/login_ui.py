import tkinter as tk
from tkinter import messagebox

import hashlib
import db

def hash_password(password:str) -> str:
    return hashlib.sha512(password.encode("utf-8")).hexdigest()

class LoginWindow:
    def __init__(self,root: tk.Tk, on_login_success):
        self.root=root
        self.on_login_success=on_login_success

        root.title("Bank Login")

        frame = tk.LabelFrame(root, text="Login/Register", padx=10, pady=10)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Username").grid(row=0, column=0,sticky="e")
        tk.Label(frame, text="Password").grid(row=1, column=0,sticky="e")

        self.entry_username = tk.Entry(frame, width=25)
        self.entry_password = tk.Entry(frame, width=25, show="*")

        self.entry_username.grid(row=0, column=1,pady=5)
        self.entry_password.grid(row=1, column=1,pady=5)

        btn_login = tk.Button(frame, text="Login",command=self.do_login)
        btn_register = tk.Button(frame,text="Register",command=self.do_register)

        btn_login.grid(row=2, column=0,pady=5)
        btn_register.grid(row=2, column=1,pady=5)

    def get_credentials(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password are both required")
            return None, None
        return username, password

    def do_login(self):
        username, password = self.get_credentials()
        if not username:
            return

        user_row=db.get_user_by_username(username)
        if not user_row:
            messagebox.showerror("Error", "Invalid username or password")
            return

        password_hash = hash_password(password)
        if user_row["password_hash"] != password_hash:
            messagebox.showerror("Error", "Invalid username or password")
            return

        self.on_login_success(user_row)

    def do_register(self):
        username, password = self.get_credentials()
        if not username:
            return

        if db.get_user_by_username(username):
            messagebox.showerror("Error", "Username already exists")
            return

        #The first user becomes admin
        is_admin = 1 if db.get_users_count() == 0 else 0

        password_hash = hash_password(password)
        db.create_user(username, password_hash, is_admin=is_admin)

        user_row = db.get_user_by_username(username)
        messagebox.showinfo(
            "Register",
            f"User '{username}' created "
            + ("Logged in as admin. " if is_admin else "User logged in.")
        )

        self.on_login_success(user_row)

        