import tkinter as tk
from tkinter import ttk

import requests

trader_token = None
widgets = {}

MY_LOANS = "https://api.spacetraders.io/my/loans"
AVAILABLE_LOANS = "https://api.spacetraders.io/types/loans"
PAY_OFF_LOAN = 'f"https://api.spacetraders.io/my/loans/{loanId}"'

proxy_workaround = {"proxies": {"http": None, "https": None}}
# proxy_workaround = {"proxies": {"https": "http://127.0.0.1:8080"}, "verify": False}


def take_out_loan(*args):
    response = requests.post(
        MY_LOANS,
        params={"token": trader_token.get(), "type": "STARTUP"},
        **proxy_workaround
    )

    if response.status_code == 422:
        error_message(response.json()["error"]["message"])


def pay_off_loan(*args):

    result = requests.get(
        MY_LOANS, params={"token": trader_token.get()}, **proxy_workaround
    )

    try:

        loanId = result.json()["loans"][0]["id"]

        pay_loan = eval(PAY_OFF_LOAN)

        response = requests.put(
            pay_loan, params={"token": trader_token.get(), "loanId": loanId}
        )

        if response.status_code == 400:
            error_message(response.json()["error"]["message"])

    except IndexError:
        error_message("You dont have any loans to pay off.")


def error_message(message):

    root = tk.Tk()
    root.title("Error Message")

    root.geometry("300x100")
    root.resizable(height=False, width=False)

    frme = ttk.Frame(root)
    frme.pack(expand=tk.YES)

    ttk.Label(frme, text=message).pack(expand=tk.YES)

    ttk.Button(frme, text="OK", command=root.destroy).pack(expand=tk.YES)

    root.mainloop()


def refresh_loans(*args):

    try:
        response = requests.get(
            MY_LOANS, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()

            widgets["current_loans_table"].delete(
                *widgets["current_loans_table"].get_children()
            )
            widgets["current_loans_table"].heading("#1", text="Type")
            widgets["current_loans_table"].heading("#2", text="Status")
            widgets["current_loans_table"].heading("#3", text="Due")
            widgets["current_loans_table"].heading("#4", text="Amount Owing")
            for row in result["loans"]:
                widgets["current_loans_table"].insert(
                    "",
                    "end",
                    text="loan_values",
                    values=(
                        row["type"],
                        row["status"],
                        row["due"],
                        row["repaymentAmount"],
                    ),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print(ce)

    try:
        response = requests.get(
            AVAILABLE_LOANS, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()

            widgets["available_loans_table"].delete(
                *widgets["available_loans_table"].get_children()
            )
            widgets["available_loans_table"].heading("#1", text="Type")
            widgets["available_loans_table"].heading("#2", text="Days")
            widgets["available_loans_table"].heading("#3", text="Rate")
            widgets["available_loans_table"].heading("#4", text="Amount")
            for row in result["loans"]:
                widgets["available_loans_table"].insert(
                    "",
                    "end",
                    text="loan_values",
                    values=(row["type"], row["termInDays"], row["rate"], row["amount"]),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print(ce)


def create_loans_tab(parent, login_token):
    global trader_token
    trader_token = login_token

    main_loan_frame = ttk.Frame(parent)

    availableLoansFrame = ttk.LabelFrame(
        main_loan_frame, text="Available Loans", relief="groove", padding=5
    )

    available_loans_table = ttk.Treeview(
        availableLoansFrame,
        height=9,
        columns=("Name", "Amount", "Rate", "Term"),
        show="headings",
    )
    widgets["available_loans_table"] = available_loans_table
    available_loans_table.column("Name", anchor=tk.W, width=80)
    available_loans_table.column("Amount", anchor=tk.W, width=80)
    available_loans_table.column("Rate", anchor=tk.W, width=80)
    available_loans_table.column("Term", anchor=tk.E, width=90)
    available_loans_table.grid(sticky=tk.NSEW)
    availableLoansFrame.grid(column=0, row=0, sticky=tk.NSEW)
    # available_loans.grid(column = 0, row = 0, sticky = NSEW)

    availableLoans_scroll = ttk.Scrollbar(
        availableLoansFrame, orient=tk.VERTICAL, command=available_loans_table.yview
    )
    availableLoans_scroll.grid(column=1, row=0, sticky=tk.NS)
    available_loans_table["yscrollcommand"] = availableLoans_scroll.set

    ttk.Button(main_loan_frame, text="Take out loan", command=take_out_loan).grid(
        column=0, row=1, sticky=tk.EW
    )

    currentLoansFrame = ttk.LabelFrame(
        main_loan_frame, text="Current Loans", relief="groove", padding=5
    )

    # current loans
    # current_loans = ttk.Frame(loans)
    current_loans_table = ttk.Treeview(
        currentLoansFrame,
        height=9,
        columns=("Name", "Amount", "Rate", "Term"),
        show="headings",
    )
    widgets["current_loans_table"] = current_loans_table
    current_loans_table.column("Name", anchor=tk.W, width=80)
    current_loans_table.column("Amount", anchor=tk.W, width=80)
    current_loans_table.column("Rate", anchor=tk.W, width=80)
    current_loans_table.column("Term", anchor=tk.E, width=90)

    current_loans_table.grid(column=0, row=0, sticky=tk.NSEW)
    currentLoansFrame.grid(column=1, row=0, sticky=tk.NSEW)
    # current_loans.grid(column = 1, row = 0, sticky = NSEW)

    currentLoans_scroll = ttk.Scrollbar(
        currentLoansFrame, orient=tk.VERTICAL, command=current_loans_table.yview
    )
    currentLoans_scroll.grid(column=1, row=0, sticky=tk.NS)
    current_loans_table["yscrollcommand"] = currentLoans_scroll.set

    ttk.Button(main_loan_frame, text="Pay off loan", command=pay_off_loan).grid(
        column=1, row=1, sticky=tk.EW
    )

    ttk.Button(parent, text="Refresh Loans", command=refresh_loans).grid(
        column=0, row=1, sticky=tk.NSEW
    )

    main_loan_frame.grid(column=0, row=0, sticky=tk.NSEW)

    availableLoansFrame.columnconfigure(0, weight=10)
    availableLoansFrame.columnconfigure(1, weight=1)
    availableLoansFrame.rowconfigure(0, weight=1)
    currentLoansFrame.columnconfigure(0, weight=10)
    currentLoansFrame.columnconfigure(1, weight=1)
    currentLoansFrame.rowconfigure(0, weight=1)

    main_loan_frame.columnconfigure(0, weight=1)
    main_loan_frame.columnconfigure(1, weight=1)
    main_loan_frame.rowconfigure(0, weight=1)

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=12)
    parent.rowconfigure(1, weight=1)


if __name__ == "__main__":

    error_message("pretend this is an error message")
