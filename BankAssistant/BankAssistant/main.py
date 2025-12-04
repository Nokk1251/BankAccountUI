import tkinter as tk

import db
from login_ui import LoginWindow
from bank_ui import BankApp

def start_app(user_row):
    login_root.destroy()
    root = tk.Tk()
    app = BankApp(root, current_user=user_row)
    root.mainloop()

if __name__ == '__main__':
    db.init_db()
    login_root = tk.Tk()
    LoginWindow(login_root,on_login_success=start_app)
    login_root.mainloop()