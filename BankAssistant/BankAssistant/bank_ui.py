import tkinter as tk
from tkinter import messagebox
from tkinter.messagebox import askyesno

from BankAccount import BankAccount
from ai_client import ask_gpt
from theme import DARK_THEME, LIGHT_THEME
import db


class BankApp:
    def __init__(self, root: tk.Tk, current_user):
        self.root = root
        self.root.title(f"Bank Account UI – {current_user['username']}")

        db.init_db()

        # Current user
        self.current_user_id = current_user["id"]
        self.current_user_name = current_user["username"]
        self.is_admin = bool(current_user["is_admin"])

        if self.is_admin:
            self.theme = DARK_THEME
        else:
            self.theme = LIGHT_THEME

        # All accounts by IBAN
        self.accounts: dict[str, BankAccount] = {}
        # Currently selected account (from the list)
        self.account: BankAccount | None = None

        # ====== Create account ======
        self.frame_account = tk.LabelFrame(root, text="Create account", padx=10, pady=10)
        self.frame_account.pack(fill="x", padx=10, pady=10)

        tk.Label(self.frame_account, text="Name").grid(row=0, column=0, sticky="e")
        tk.Label(self.frame_account, text="IBAN").grid(row=1, column=0, sticky="e")
        tk.Label(self.frame_account, text="Initial Balance").grid(row=2, column=0, sticky="e")
        tk.Label(self.frame_account, text="Overdraft Limit").grid(row=3, column=0, sticky="e")

        self.entry_name = tk.Entry(self.frame_account, width=25)
        self.entry_iban = tk.Entry(self.frame_account, width=25)
        self.entry_balance = tk.Entry(self.frame_account, width=25)
        self.entry_overdraft_limit = tk.Entry(self.frame_account, width=25)

        self.entry_name.grid(row=0, column=1)
        self.entry_iban.grid(row=1, column=1)
        self.entry_balance.grid(row=2, column=1)
        self.entry_overdraft_limit.grid(row=3, column=1)

        self.btn_create = tk.Button(self.frame_account, text="Create",
                                    command=self.create_account)
        self.btn_create.grid(row=4, column=0, columnspan=2, pady=5)

        # ====== Account list ======
        self.frame_list = tk.LabelFrame(root, text="Account")
        self.frame_list.pack(fill="x", padx=10, pady=5)

        self.list_accounts = tk.Listbox(self.frame_list, height=5, width=35)
        self.list_accounts.pack(side="left", padx=5, pady=5)

        # When selection in the listbox changes
        self.list_accounts.bind("<<ListboxSelect>>", self.on_select_account)

        # ====== Options (deposit / withdraw) ======
        self.frame_ops = tk.LabelFrame(root, text="Options")
        self.frame_ops.pack(fill="x", padx=10, pady=10)

        tk.Label(self.frame_ops, text="Amount").grid(row=0, column=0)
        self.entry_amount = tk.Entry(self.frame_ops, width=20)
        self.entry_amount.grid(row=0, column=1)

        self.btn_deposit = tk.Button(
            self.frame_ops, text="Deposit", state="disabled", command=self.do_deposit
        )
        self.btn_withdraw = tk.Button(
            self.frame_ops, text="Withdraw", state="disabled", command=self.do_withdraw
        )

        self.btn_deposit.grid(row=1, column=0, pady=5)
        self.btn_withdraw.grid(row=1, column=1, pady=5)

        # ====== Details / History / Reset / Delete ======
        self.frame_cred = tk.LabelFrame(root, text="Show Details")
        self.frame_cred.pack(fill="x", padx=10, pady=10)

        tk.Label(self.frame_cred, text="Details").grid(row=0, column=0)
        self.btn_details = tk.Button(
            self.frame_cred, text="Show details",
            state="disabled", command=self.show_details
        )
        self.btn_details.grid(row=0, column=2, columnspan=2, pady=5)

        tk.Label(self.frame_cred, text="History").grid(row=1, column=0)
        self.btn_history = tk.Button(
            self.frame_cred, text="Show history",
            state="disabled", command=self.show_history
        )
        self.btn_history.grid(row=1, column=2, columnspan=2, pady=5)

        tk.Label(self.frame_cred, text="Reset").grid(row=2, column=0)
        self.btn_reset = tk.Button(
            self.frame_cred, text="Reset account",
            state="disabled", command=self.reset_account
        )
        self.btn_reset.grid(row=2, column=2, columnspan=2, pady=5)

        tk.Label(self.frame_cred, text="Delete").grid(row=3, column=0)
        self.btn_delete = tk.Button(
            self.frame_cred, text="Delete account",
            state="disabled", command=self.delete_account
        )
        self.btn_delete.grid(row=3, column=2, columnspan=2, pady=5)

        # ====== Assistant ======
        self.frame_ai = tk.LabelFrame(root, text="Assistant")
        self.frame_ai.pack(fill="x", padx=10, pady=10)

        tk.Label(self.frame_ai, text="Ask:").grid(row=0, column=0, sticky="e")
        self.entry_question = tk.Entry(self.frame_ai, width=30)
        self.entry_question.grid(row=0, column=1, padx=5, pady=5)

        self.btn_ask = tk.Button(
            self.frame_ai, text="Ask assistant",
            state="disabled", command=self.ask_assistant
        )
        self.btn_ask.grid(row=0, column=2, padx=5, pady=5)

        # ====== Status ======
        self.label_status = tk.Label(root, text="No account created yet.")
        self.label_status.pack(fill="x", padx=10, pady=5)

        role_text = "admin" if self.is_admin else "user"
        self.label_user = tk.Label(root, text=f"Logged in as {self.current_user_name} (role: {role_text})")
        self.label_user.pack(fill="x",padx=10,pady=5)

        self.label_summary = tk.Label(root, text="")
        self.label_summary.pack(fill="x",padx=10,pady=(0,10))

        self._load_accounts_from_db()
        self._apply_theme()

    # ---------- helper for enabling/disabling buttons ----------
    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in [
            self.btn_deposit, self.btn_withdraw,
            self.btn_details, self.btn_history,
            self.btn_reset, self.btn_delete, self.btn_ask,
        ]:
            btn.config(state=state)

    #---------- applying the theme ----------
    def _apply_theme(self):
        t = self.theme

        self.root.configure(bg=t["bg"])

        self.label_status.config(bg=t["status_bg"], fg=t["status_fg"])

        def style_children(widget):
            for child in widget.winfo_children():
                #LabelFrame
                if isinstance(child, tk.LabelFrame):
                    child.configure(bg=t["frame_bg"], fg=t["fg"])
                    style_children(child)

                #Frame
                elif isinstance(child, tk.Frame):
                    child.configure(bg=t["frame_bg"])
                    style_children(child)

                #Label
                elif isinstance(child, tk.Label):
                    child.configure(bg=t["frame_bg"], fg=t["fg"])

                #Button
                elif isinstance(child, tk.Button):
                    child.configure(bg=t["button_bg"], fg=t["button_fg"],activebackground=t["accent"],activeforeground=t["bg"],borderwidth=1,highlightbackground=t["frame_bg"],highlightthickness=0)

                #Entry
                elif isinstance(child, tk.Entry):
                    child.configure(bg=t["entry_bg"],fg=t["entry_fg"],insertbackground=t["entry_fg"], borderwidth=1,highlightbackground=t["frame_bg"],highlightthickness=0)

                #Listbox
                elif isinstance(child, tk.Listbox):
                    child.configure(bg=t["listbox_bg"],fg=t["listbox_fg"],selectbackground=t["frame_bg"],selectforeground=t["accent"],borderwidth=1,highlightbackground=t["frame_bg"],highlightthickness=0)

                else:
                    style_children(child)

        style_children(self.root)



    # ---------- clearing entries ----------
    def _clear_create_fields(self):
        for entry in [
            self.entry_name,
            self.entry_iban,
            self.entry_balance,
            self.entry_overdraft_limit,
        ]:
            entry.delete(0, tk.END)

    # ---------- accounts summary ----------
    def _update_summary(self):
        total_accounts = len(self.accounts)
        total_balance = sum(acc.balance for acc in self.accounts.values())

        if self.is_admin:
            text = f"Total accounts: {total_accounts} | Total balance for all accounts {total_balance:.2f}"
        else:
            text = f"Your accounts: {total_accounts} | Total balance {total_balance:.2f}"

        self.label_summary.config(text=text)

    # ---------- account creation ----------
    def create_account(self):
        name = self.entry_name.get().strip()
        iban = self.entry_iban.get().strip()
        bal_text = self.entry_balance.get().strip()
        overdraft_text = self.entry_overdraft_limit.get().strip()

        # Overdraft validation (can be empty or <= 0)
        if overdraft_text == "":
            overdraft_limit = 0.0
        else:
            try:
                overdraft_limit = float(overdraft_text.replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Overdraft must be a number")
                return
            if overdraft_limit > 0:
                messagebox.showerror("Error", "Overdraft must be <= 0")
                return

        # Balance validation
        try:
            balance = float(bal_text.replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Balance must be a number")
            return

        # Create actual BankAccount model
        try:
            self.account = BankAccount(name, balance, iban, overdraft_limit,user_name=self.current_user_name)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            acc_id = db.create_account(
                self.account.owner,
                self.account.iban,
                self.account.balance,
                self.account.overdraft_limit,
                self.current_user_id,
            )
            self.account.db_id = acc_id

            from BankAccount import Transaction
            open_tx = Transaction("OPEN",0,self.account.balance,"account balance")
            self.account.transactions.append(open_tx)
            db.add_transaction(acc_id,open_tx.t_type,open_tx.amount,open_tx.balance_after,open_tx.details,)


        except Exception as e:
            messagebox.showerror("DB Error", f"Could not create account: {e}")
            return


        # Store in dictionary by IBAN
        self.accounts[iban] = self.account



        # Update status + enable buttons
        self.label_status.config(
            text=(
                f"Account created. Balance: {self.account.balance:.2f} "
                f"with an overdraft of {self.account.overdraft_limit:.2f}"
            )
        )
        self._set_buttons_enabled(True)
        self.refresh_account_list()
        self._update_summary()
        self._clear_create_fields()

    # ---------- amount parsing ----------
    def _get_amount(self):
        try:
            return float(self.entry_amount.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return None

    # ---------- operations ----------
    def do_deposit(self):
        if self.account is None:
            return
        amount = self._get_amount()
        if amount is None:
            return

        try:
            self.account.deposit(amount)
            self.label_status.config(text=f"Balance: {self.account.balance:.2f}")

            if self.account.db_id is not None:
                db.update_account_balance(self.account.db_id, self.account.balance)
                last_tx = self.account.transactions[-1]
                db.add_transaction(self.account.db_id,last_tx.t_type,last_tx.amount,last_tx.balance_after,last_tx.details,)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        self._update_summary()

    def do_withdraw(self):
        if self.account is None:
            return
        amount = self._get_amount()
        if amount is None:
            return
        try:
            self.account.withdraw(amount)
            self.label_status.config(text=f"Balance: {self.account.balance:.2f}")

            if self.account.db_id is not None:
                db.update_account_balance(self.account.db_id, self.account.balance)
                last_tx = self.account.transactions[-1]
                db.add_transaction(
                    self.account.db_id,
                    last_tx.t_type,
                    last_tx.amount,
                    last_tx.balance_after,
                    last_tx.details,
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))
        self._update_summary()


    # ---------- details / history ----------
    def show_details(self):
        if self.account is None:
            return
        messagebox.showinfo("Details", str(self.account))

    def show_history(self):
        if self.account is None:
            messagebox.showerror("Error", "Account not created")
            return

        if self.account.db_id is None:
            messagebox.showinfo("History", "No history in database for this account.")
            return

        rows = db.load_transactions_for_account(self.account.db_id)
        if not rows:
            messagebox.showinfo("History", "No transactions yet.")
            return

        lines = []
        for row in rows:
            created = row["created_at"]
            t_type = row["t_type"].ljust(12)
            amount = row["amount"]
            balance_after = row["balance_after"]
            details = row["details"] or ""
            line = (
                f"{created} | {t_type} {amount:10.2f} -> "
                f"balance {balance_after:>10.2f} {details}"
            )
            lines.append(line)

        text = "\n".join(lines)
        messagebox.showinfo("History", text)

    # ---------- reset UI ----------
    def reset_account(self):
        """Reset UI fields and selection, but do NOT delete accounts."""
        self.account = None

        for entry in [
            self.entry_name, self.entry_iban,
            self.entry_balance, self.entry_amount,
            self.entry_question, self.entry_overdraft_limit,
        ]:
            entry.delete(0, tk.END)

        self.list_accounts.selection_clear(0, tk.END)
        self._set_buttons_enabled(False)
        self.label_status.config(text="No account created yet. Balance: 0.00")

    # ---------- listbox helpers ----------
    def refresh_account_list(self):
        """Reload listbox from self.accounts."""
        self.list_accounts.delete(0, tk.END)
        for iban, acc in self.accounts.items():
            if self.is_admin:
                label = f"{iban} | {acc.owner} | {acc.user_name}"
            else:
                label = f"{iban} | {acc.owner}"
            self.list_accounts.insert(tk.END, label)

    def on_select_account(self, event):
        """When a listbox row is selected – switch current account."""
        if not self.list_accounts.curselection():
            return

        index = self.list_accounts.curselection()[0]
        label = self.list_accounts.get(index)   # e.g. "BG11... | Nikola"
        iban = label.split("|", 1)[0].strip()

        acc = self.accounts.get(iban)
        if not acc:
            return

        self.account = acc
        self.label_status.config(
            text=(
                f"Selected {iban}. "
                f"Balance: {self.account.balance:.2f} "
                f"with an overdraft of {self.account.overdraft_limit:.2f}"
            )
        )
        self._set_buttons_enabled(True)

    # ---------- delete account ----------
    def delete_account(self):
        if self.account is None:
            messagebox.showerror("Error", "No account selected")
            return

        iban = self.account.iban
        acc_db_id = self.account.db_id

        confirmed = askyesno(
            "Confirm",
            f"Are you sure you want to delete account {iban}?"
        )
        if not confirmed:
            return

        if acc_db_id is not None:
            db.delete_account(acc_db_id)

        if iban in self.accounts:
            del self.accounts[iban]

        self.account = None
        self.refresh_account_list()
        self._update_summary()

        if self.accounts:
            # Select the first remaining account
            next_iban = next(iter(self.accounts))
            self.account = self.accounts[next_iban]
            self.label_status.config(
                text=f"Selected {next_iban}. Balance: {self.account.balance:.2f}"
            )
            self._set_buttons_enabled(True)
        else:
            # No accounts left – clear UI
            for entry in [
                self.entry_name, self.entry_iban,
                self.entry_balance, self.entry_amount,
                self.entry_question, self.entry_overdraft_limit,
            ]:
                entry.delete(0, tk.END)
            self._set_buttons_enabled(False)
            self.label_status.config(text="No account created yet. Balance: 0.00")
        self._update_summary()

    def _load_accounts_from_db(self):
        rows = db.load_accounts_for_user(
            user_id = self.current_user_id,
            is_admin = self.is_admin,
        )
        self.accounts.clear()
        for row in rows:
            acc = BankAccount(
                owner = row["owner"],
                balance = row["balance"],
                iban = row["iban"],
                overdraft_limit = row["overdraft_limit"],
                db_id=row["account_id"],
            )
            acc.user_name = row["user_name"]
            self.accounts[acc.iban] = acc
        self.refresh_account_list()
        self._update_summary()


    # ---------- fake AI assistant + GPT ----------
    def ask_assistant(self):
        if self.account is None:
            messagebox.showerror("Error", "Account not created")
            return

        text = self.entry_question.get().strip()
        if not text:
            messagebox.showerror("Error", "Question cannot be empty")
            return

        # lower-case for command detection
        q = text.lower()

        # --- basic command rules (work directly with the model) ---

        # balance
        if q == "balance" or q.startswith("balance ") \
                or q == "баланс" or q.startswith("баланс "):
            msg = (
                f"Current account {self.account.owner} "
                f"({self.account.iban}) has a balance of "
                f"{self.account.balance:.2f}"
            )
            messagebox.showinfo("Assistant", message=msg)

        # deposit X
        elif q.startswith("deposit"):
            parts = q.split()
            if len(parts) < 2:
                messagebox.showerror("Assistant", "Use: deposit <amount>")
            else:
                self.entry_amount.delete(0, tk.END)
                self.entry_amount.insert(0, parts[1])
                self.do_deposit()

        # withdraw X
        elif q.startswith("withdraw"):
            parts = q.split()
            if len(parts) < 2:
                messagebox.showerror("Assistant", "Use: withdraw <amount>")
            else:
                self.entry_amount.delete(0, tk.END)
                self.entry_amount.insert(0, parts[1])
                self.do_withdraw()

        # history
        elif "history" in q or "история" in q:
            self.show_history()

        # owner
        elif "owner" in q or "собственик" in q:
            msg = f"Current account owner: {self.account.owner}"
            messagebox.showinfo("Assistant", message=msg)

        # IBAN
        elif q.startswith("iban"):
            msg = f"Current IBAN: {self.account.iban}"
            messagebox.showinfo("Assistant", message=msg)

        # reset UI
        elif q.startswith("reset"):
            self.reset_account()
            messagebox.showinfo("Assistant", "Account UI has been reset.")

            # set overdraft X
        elif q.startswith("set overdraft"):
            parts = q.split()
            if len(parts) < 3:
                messagebox.showerror("Assistant", "Use: set overdraft <amount>")
            else:
                try:
                    amount = float(parts[2].replace(",", "."))
                except ValueError:
                    messagebox.showerror("Assistant", "Overdraft must be a number")
                    return

                if amount > 0:
                    messagebox.showerror("Assistant", "Overdraft must be <= 0")
                    return

                self.account.overdraft_limit = amount

                if self.account.db_id is not None:
                    db.update_overdraft(self.account.db_id,amount)

                self.label_status.config(
                    text=(
                        f"Selected {self.account.iban}. "
                        f"Balance: {self.account.balance:.2f} "
                        f"with an overdraft of {self.account.overdraft_limit:.2f}"
                    )
                )
                messagebox.showinfo(
                    "Assistant",
                    f"Overdraft set to {self.account.overdraft_limit:.2f}",
                )

        # show overdraft
        elif q == "overdraft" or q.startswith("overdraft ") \
                or q == "овърдрафт" or q.startswith("овърдрафт "):
            msg = f"Current overdraft limit is {self.account.overdraft_limit:.2f}"
            messagebox.showinfo("Assistant", message=msg)

        # GPT fallback
        else:
            prompt = (
                "You are a banking assistant inside a small desktop demo app.\n"
                "You can NOT actually move real money, but you can explain things.\n"
                "Current account:\n"
                f"- Owner: {self.account.owner}\n"
                f"- IBAN: {self.account.iban}\n"
                f"- Balance: {self.account.balance:.2f}\n"
                f"- Overdraft limit: {self.account.overdraft_limit:.2f}\n\n"
                f"User question: {text}\n\n"
                "Answer briefly and clearly. If the user asks to deposit or withdraw, "
                "explain what would happen, but do not say that you executed it yourself."
            )

            answer = ask_gpt(prompt)

            if answer.startswith("[OpenAI error]"):
                messagebox.showerror("Assistant", answer)
            else:
                messagebox.showinfo("Assistant", answer)
