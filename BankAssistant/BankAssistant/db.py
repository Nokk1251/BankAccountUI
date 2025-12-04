import sqlite3
from pathlib import Path

DB_FILE = "bank.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            iban TEXT NOT NULL UNIQUE,
            balance REAL NOT NULL,
            overdraft_limit REAL NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            t_type TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_after REAL NOT NULL,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );
            
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount REAL NOT NULL,
            is_paid INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
        );   
        """
    )

    conn.commit()
    conn.close()


def create_account(owner: str, iban: str, balance: float, overdraft_limit: float, user_id: int, ) -> int:
    """Insert a new account and return its DB id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO accounts (owner, iban, balance, overdraft_limit, user_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (owner, iban, balance, overdraft_limit, user_id),
    )
    conn.commit()
    account_id = cur.lastrowid
    conn.close()
    return account_id


def load_accounts_for_user(user_id: int, is_admin: bool):
    conn = get_connection()
    cur = conn.cursor()
    if is_admin:
        cur.execute(
            "SELECT a.id as account_id, a.owner, a.iban, a.balance, a.overdraft_limit, a.user_id, u.username AS user_name FROM accounts a JOIN users u ON a.user_id = u.id ORDER BY a.id"
        )
    else:
        cur.execute(
            "SELECT a.id as account_id, a.owner, a.iban, a.balance, a.overdraft_limit, a.user_id, u.username AS user_name FROM accounts a JOIN users u ON a.user_id = u.id WHERE a.user_id = ? ORDER BY a.id",
            (user_id,),
            )

    rows = cur.fetchall()
    conn.close()
    return rows


def update_account_balance(account_id: int, new_balance: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (new_balance, account_id),
    )
    conn.commit()
    conn.close()


def add_transaction(
        account_id: int,
        t_type: str,
        amount: float,
        balance_after: float,
        details: str = "",
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO transactions (account_id, t_type, amount, balance_after, details)
        VALUES (?, ?, ?, ?, ?)
        """,
        (account_id, t_type, amount, balance_after, details),
    )
    conn.commit()
    conn.close()


def load_transactions_for_account(account_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t_type, amount, balance_after, details, created_at
        FROM TRANSACTIONS
        WHERE account_id = ?
        ORDER BY id
        """,
        (account_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def add_bill(account_id: int, title:str, due_date: str, amount: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bills (account_id, title, due_date, amount)
        VALUES(?,?,?,?)
        """,
        (account_id,title,due_date,amount),
    )
    conn.commit()
    conn.close()

def load_bills_for_account(account_id: int, only_unpaid: bool = True):
    conn = get_connection()
    cur = conn.cursor()
    if only_unpaid:
        cur.execute(
            """
            SELECT id, title, due_date, amount, is_paid FROM bills WHERE account_id = ? and is_paid = 0 ORDER BY due_date
            """,
            (account_id,),
        )
    else:
        cur.execute(
            """
            SELECT id, title, due_date, amount, is_paid FROM bills WHERE account_id = ? ORDER BY due_date
            """,
            (account_id,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows

def mark_bill_paid(bill_id: int):
    conn= get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE bills SET is_paid = 1 WHERE id = ?",
        (bill_id,),
    )
    conn.commit()
    conn.close()

def delete_account(account_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()


def update_overdraft(account_id: int, new_limit: float):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET overdraft_limit = ? WHERE id = ?",
                (new_limit, account_id), )
    conn.commit()
    conn.close()


def create_user(username: str, password_hash: str, is_admin: int = 0) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (username, password_hash, is_admin)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, is_admin),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_users_count() -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT (*) AS usr FROM users")
    row = cur.fetchone()
    conn.close()
    return row["usr"] if row else 0