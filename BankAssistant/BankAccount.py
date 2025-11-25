class BankAccount:
    def __init__(self, owner, balance, iban, overdraft_limit=0):
        # Owner validation
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Owner must be a non-empty string.")

        # Initial balance must be non-negative number
        if not isinstance(balance, (int, float)) or balance < 0:
            raise ValueError("Initial balance must be a non-negative number.")

        # IBAN validation
        if not isinstance(iban, str) or not iban.strip():
            raise ValueError("IBAN must be a non-empty string.")

        # Overdraft limit must be <= 0
        if not isinstance(overdraft_limit, (int, float)) or overdraft_limit > 0:
            raise ValueError("Initial overdraft limit must be a negative number or zero.")

        self.owner = owner.strip()
        self.balance = round(float(balance), 2)
        self.iban = iban.strip()
        self.transactions = []      # list[Transaction]
        self.overdraft_limit = overdraft_limit

    def deposit(self, amount):
        """Deposit money into the account."""
        if not isinstance(amount, (int, float)):
            print("Amount must be a number.")
            return
        if amount <= 0:
            print("Amount must be greater than 0.")
            return

        self.balance = round(self.balance + amount, 2)
        print(f"Deposited: {amount:.2f}. New balance: {self.balance:.2f}.")
        self.transactions.append(
            Transaction("DEPOSIT", amount, self.balance, "cash deposit")
        )

    def withdraw(self, amount):
        """Withdraw money, respecting the overdraft limit."""
        if not isinstance(amount, (int, float)):
            print("Amount must be a number.")
            return
        if amount <= 0:
            print("Amount must be greater than 0.")
            return
        if self.balance - amount < self.overdraft_limit:
            print(
                f"Insufficient balance. Overdraft limit reached. "
                f"Current balance: {self.balance:.2f}."
            )
            return

        self.balance = round(self.balance - amount, 2)
        print(f"Withdrew: {amount:.2f}. Remaining balance: {self.balance:.2f}.")
        self.transactions.append(
            Transaction("WITHDRAW", amount, self.balance, "cash withdraw")
        )

    def transfer_to(self, other_account, amount):
        """Transfer money to another BankAccount."""
        if not isinstance(other_account, BankAccount):
            print("Target must be a BankAccount.")
            return

        if not isinstance(amount, (int, float)):
            print("Amount must be a number.")
            return

        if amount <= 0:
            print("Amount must be greater than 0.")
            return

        if self.balance - amount < self.overdraft_limit:
            print(
                f"Insufficient balance. Overdraft limit reached. "
                f"Current balance: {self.balance:.2f}."
            )
            return

        # Perform transfer
        self.balance = round(self.balance - amount, 2)
        other_account.balance = round(other_account.balance + amount, 2)

        # Add history entries on both sides
        self.transactions.append(
            Transaction("TRANSFER_OUT", amount, self.balance,
                        f"to {other_account.iban}")
        )
        other_account.transactions.append(
            Transaction("TRANSFER_IN", amount, other_account.balance,
                        f"from {self.iban}")
        )

        print(f"Transferred {amount:.2f} from {self.iban} to {other_account.iban}.")

    def print_history(self):
        """Print transaction history to the console."""
        if not self.transactions:
            print("No transactions.")
            return

        print(f"Transaction history for {self.owner}:")
        for t in self.transactions:
            print(" -", t)

    def to_dict(self) -> dict:
        """Serialize account to a plain dict (for JSON, etc.)."""
        return {
            "owner": self.owner,
            "balance": float(self.balance),
            "iban": self.iban,
            "overdraft_limit": float(self.overdraft_limit),
            "transactions": [t.to_dict() for t in self.transactions],
        }

    def __str__(self):
        return (
            f"Account(owner={self.owner}, "
            f"IBAN={self.iban}, balance={self.balance:.2f}, "
            f"overdraft={self.overdraft_limit:.2f})"
        )


class Transaction:
    def __init__(self, t_type, amount, balance_after, details=""):
        if not isinstance(t_type, str) or not t_type.strip():
            raise ValueError("Transaction type must be a non-empty string.")
        if not isinstance(amount, (int, float)) or amount < 0:
            raise ValueError("Amount must be a positive number.")
        if not isinstance(balance_after, (int, float)):
            raise ValueError("Balance must be a number.")

        self.t_type = t_type.strip().upper()
        self.amount = amount
        self.balance_after = balance_after
        self.details = details

    def to_dict(self) -> dict:
        return {
            "type": self.t_type,
            "amount": float(self.amount),
            "balance_after": float(self.balance_after),
            "details": self.details,
        }

    def __str__(self):
        return (
            f"{self.t_type} {self.amount:.2f} -> "
            f"balance {self.balance_after:.2f} {self.details}"
        )
