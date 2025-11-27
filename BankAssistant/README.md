1. Bank Account UI (Python + Tkinter)

This is still a very basic project I did while playing around and learning Python and Tkinter. It lets you create multiple bank accounts, work with balances and overdraft, and play with a simple “assistant” that understands text commands like `deposit 50` or `balance` and now has an integrated AI assistant that requires an API key from OpenAI to work. 


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
- Real AI assistant

---

3. Tech stack

- **Python 3**
- **Tkinter** for the UI
- Plain Python classes for the account logic (`BankAccount` and `Transaction`)
- OpenAI API for the AI assistant

The logic and the interface are kept in separate files:

- `BankAccount.py` – account and transaction logic
- `bank_ui.py` – Tkinter user interface

---

4. How to run

-1. Install **Python 3** (on Windows it’s usually available as `py` or `python` in the terminal).
-2. Download or clone this repository:
   - either use the **“Code → Download ZIP”** button,  
   - or run:
-3 AI setup(optional)
*The app can work without AI, but if you want to use it, you will need an OpenAI API key.

 Steps:
	I. Create an account at the OpenAI platform and generate your API key.
	II. There is an example file I created called "config.example.py" which is where you will need to place your API key.
	III. After placing your API key make a copy of the file and rename it to just "config.py"

	It is also important to say that "config.py" is ignored by git on purpose, so your key stays private.

Skipping these steps won't really affect the "bank" it will just work without the AI.

	

5.Notes

This is a learning project, not a real banking app.
I use it mainly to practice:

separating UI from business logic

working with multiple objects (accounts) in a dictionary

basic Tkinter layout and event handling

simple “assistant” logic based on text commands