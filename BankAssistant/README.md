1. Bank Account UI (Python + Tkinter)

Small desktop app I wrote while learning Python and Tkinter.  
It lets you create multiple bank accounts, work with balances and overdraft, and play with a simple “assistant” that understands text commands like `deposit 50` or `balance`.


2. Features

- Create bank accounts with:
  - owner name
  - IBAN
  - initial balance
  - overdraft limit (can be 0 or a negative number)
- Multiple accounts in one window (account list on the left)
- Deposit and withdraw money with validation
- Overdraft limit checks on withdraw
- Transaction history (stored in memory for each account)
- Delete account with confirmation dialog
- Simple “fake AI assistant”:
  - understands commands like `deposit 100`, `withdraw 50`, `balance`
  - can show history, owner, IBAN and overdraft
  - can change the overdraft with `set overdraft -500`

---

3. Tech stack

- **Python 3**
- **Tkinter** for the desktop UI
- Plain Python classes for the account logic (`BankAccount` and `Transaction`)

The logic and the interface are kept in separate files:

- `BankAccount.py` – account and transaction logic
- `bank_ui.py` – Tkinter user interface

---

4. How to run

-1. Install **Python 3** (on Windows it’s usually available as `py` or `python` in the terminal).
-2. Download or clone this repository:
   - either use the **“Code → Download ZIP”** button,  
   - or run:

5.Notes

This is a learning project, not a real banking app.
I use it mainly to practice:

separating UI from business logic

working with multiple objects (accounts) in a dictionary

basic Tkinter layout and event handling

simple “assistant” logic based on text commands