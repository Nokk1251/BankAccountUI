import tkinter as tk
from tkinter import messagebox
from tkinter.messagebox import askyesno

from BankAccount import BankAccount


class BankApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bank Account UI")

        # All accounts by IBAN
        self.accounts: dict[str, BankAccount] = {}
        # Currently selected account (from the list)
        self.account: BankAccount | None = None

        # ====== Create account ======
        frame_account = tk.LabelFrame(root, text="Create account", padx=10, pady=10)
        frame_account.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_account, text="Name").grid(row=0, column=0, sticky="e")
        tk.Label(frame_account, text="IBAN").grid(row=1, column=0, sticky="e")
        tk.Label(frame_account, text="Initial Balance").grid(row=2, column=0, sticky="e")
        tk.Label(frame_account, text="Overdraft Limit").grid(row=3, column=0, sticky="e")

        self.entry_name = tk.Entry(frame_account, width=25)
        self.entry_iban = tk.Entry(frame_account, width=25)
        self.entry_balance = tk.Entry(frame_account, width=25)
        self.entry_overdraft_limit = tk.Entry(frame_account, width=25)

        self.entry_name.grid(row=0, column=1)
        self.entry_iban.grid(row=1, column=1)
        self.entry_balance.grid(row=2, column=1)
        self.entry_overdraft_limit.grid(row=3, column=1)

        self.btn_create = tk.Button(frame_account, text="Create",
                                    command=self.create_account)
        self.btn_create.grid(row=4, column=0, columnspan=2, pady=5)

        # ====== Account list ======
        frame_list = tk.LabelFrame(root, text="Account")
        frame_list.pack(fill="x", padx=10, pady=5)

        self.list_accounts = tk.Listbox(frame_list, height=5, width=35)
        self.list_accounts.pack(side="left", padx=5, pady=5)

        # When selection in the listbox changes
        self.list_accounts.bind("<<ListboxSelect>>", self.on_select_account)

        # ====== Options (deposit / withdraw) ======
        frame_ops = tk.LabelFrame(root, text="Options")
        frame_ops.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_ops, text="Amount").grid(row=0, column=0)
        self.entry_amount = tk.Entry(frame_ops, width=20)
        self.entry_amount.grid(row=0, column=1)

        self.btn_deposit = tk.Button(
            frame_ops, text="Deposit", state="disabled", command=self.do_deposit
        )
        self.btn_withdraw = tk.Button(
            frame_ops, text="Withdraw", state="disabled", command=self.do_withdraw
        )

        self.btn_deposit.grid(row=1, column=0, pady=5)
        self.btn_withdraw.grid(row=1, column=1, pady=5)

        # ====== Details / History / Reset / Delete ======
        frame_cred = tk.LabelFrame(root, text="Show Details")
        frame_cred.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_cred, text="Details").grid(row=0, column=0)
        self.btn_details = tk.Button(
            frame_cred, text="Show details",
            state="disabled", command=self.show_details
        )
        self.btn_details.grid(row=0, column=2, columnspan=2, pady=5)

        tk.Label(frame_cred, text="History").grid(row=1, column=0)
        self.btn_history = tk.Button(
            frame_cred, text="Show history",
            state="disabled", command=self.show_history
        )
        self.btn_history.grid(row=1, column=2, columnspan=2, pady=5)

        tk.Label(frame_cred, text="Reset").grid(row=2, column=0)
        self.btn_reset = tk.Button(
            frame_cred, text="Reset account",
            state="disabled", command=self.reset_account
        )
        self.btn_reset.grid(row=2, column=2, columnspan=2, pady=5)

        tk.Label(frame_cred, text="Delete").grid(row=3, column=0)
        self.btn_delete = tk.Button(
            frame_cred, text="Delete account",
            state="disabled", command=self.delete_account
        )
        self.btn_delete.grid(row=3, column=2, columnspan=2, pady=5)

        # ====== Assistant ======
        frame_ai = tk.LabelFrame(root, text="Assistant")
        frame_ai.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_ai, text="Ask:").grid(row=0, column=0, sticky="e")
        self.entry_question = tk.Entry(frame_ai, width=30)
        self.entry_question.grid(row=0, column=1, padx=5, pady=5)

        self.btn_ask = tk.Button(
            frame_ai, text="Ask assistant",
            state="disabled", command=self.ask_assistant
        )
        self.btn_ask.grid(row=0, column=2, padx=5, pady=5)

        # ====== Status ======
        self.label_status = tk.Label(root, text="No account created yet.")
        self.label_status.pack(fill="x", padx=10, pady=5)

    # ---------- helper for enabling/disabling buttons ----------
    def _set_buttons_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in [
            self.btn_deposit, self.btn_withdraw,
            self.btn_details, self.btn_history,
            self.btn_reset, self.btn_delete, self.btn_ask,
        ]:
            btn.config(state=state)

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
            self.account = BankAccount(name, balance, iban, overdraft_limit)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Store in dictionary by IBAN
        self.accounts[iban] = self.account

        # Refresh listbox
        self.refresh_account_list()

        # Update status + enable buttons
        self.label_status.config(
            text=(
                f"Account created. Balance: {self.account.balance:.2f} "
                f"with an overdraft of {self.account.overdraft_limit:.2f}"
            )
        )
        self._set_buttons_enabled(True)

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
        self.account.deposit(amount)
        self.label_status.config(text=f"Balance: {self.account.balance:.2f}")

    def do_withdraw(self):
        if self.account is None:
            return
        amount = self._get_amount()
        if amount is None:
            return
        try:
            self.account.withdraw(amount)
            self.label_status.config(text=f"Balance: {self.account.balance:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- details / history ----------
    def show_details(self):
        if self.account is None:
            return
        messagebox.showinfo("Details", str(self.account))

    def show_history(self):
        if self.account is None:
            messagebox.showerror("Error", "Account not created")
            return

        if not self.account.transactions:
            messagebox.showinfo("History", "No transactions yet.")
            return

        lines = [str(t) for t in self.account.transactions]
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

        confirmed = askyesno(
            "Confirm",
            f"Are you sure you want to delete account {iban}?"
        )
        if not confirmed:
            return

        if iban in self.accounts:
            del self.accounts[iban]

        self.account = None
        self.refresh_account_list()

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

    # ---------- fake AI assistant ----------
    def ask_assistant(self):
        if self.account is None:
            messagebox.showerror("Error", "Account not created")
            return

        text = self.entry_question.get().strip()
        if not text:
            messagebox.showerror("Error", "Question cannot be empty")
            return

        q = text.lower()

        # balance
        if "balance" in q or "баланс" in q:
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
                try:
                    amount = float(parts[1].replace(",", "."))
                    self.account.deposit(amount)
                    self.label_status.config(
                        text=f"Balance: {self.account.balance:.2f}"
                    )
                    messagebox.showinfo("Assistant", f"Deposited {amount:.2f}")
                except ValueError as e:
                    messagebox.showerror("Assistant", str(e))

        # withdraw X
        elif q.startswith("withdraw"):
            parts = q.split()
            if len(parts) < 2:
                messagebox.showerror("Assistant", "Use: withdraw <amount>")
            else:
                try:
                    amount = float(parts[1].replace(",", "."))
                    self.account.withdraw(amount)
                    self.label_status.config(
                        text=f"Balance: {self.account.balance:.2f}"
                    )
                    messagebox.showinfo("Assistant", f"Withdrawn {amount:.2f}")
                except ValueError as e:
                    messagebox.showerror("Assistant", str(e))

        # history
        elif "history" in q or "история" in q:
            self.show_history()

        # owner
        elif "owner" in q or "собственик" in q:
            msg = f"Current account owner: {self.account.owner}"
            messagebox.showinfo("Assistant", message=msg)

        # IBAN
        elif "iban" in q or "ибан" in q:
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
                messagebox.showerror(
                    "Assistant", "Use: set overdraft <amount>"
                )
            else:
                try:
                    amount = float(parts[2].replace(",", "."))
                except ValueError:
                    messagebox.showerror(
                        "Assistant", "Overdraft must be a number"
                    )
                    return

                if amount > 0:
                    messagebox.showerror(
                        "Assistant", "Overdraft must be <= 0"
                    )
                    return

                self.account.overdraft_limit = amount
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
        elif "overdraft" in q or "овърдрафт" in q:
            msg = f"Current overdraft limit is {self.account.overdraft_limit:.2f}"
            messagebox.showinfo("Assistant", message=msg)

        # fallback
        else:
            messagebox.showinfo(
                "Assistant",
                "I understand commands like:\n"
                "- 'balance'          -> show current balance\n"
                "- 'deposit X'        -> deposit amount X\n"
                "- 'withdraw X'       -> withdraw amount X\n"
                "- 'overdraft'        -> show overdraft limit\n"
                "- 'set overdraft X'  -> set overdraft limit\n"
                "- 'history'          -> show account history\n"
                "- 'owner'            -> show account owner\n"
                "- 'iban'             -> show IBAN\n"
                "- 'reset'            -> reset UI state\n",
            )


if __name__ == "__main__":
    root = tk.Tk()
    BankApp(root)
    root.mainloop()