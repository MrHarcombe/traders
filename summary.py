import tkinter as tk
from tkinter import ttk

import requests

import util

MY_ACCOUNT = "https://api.spacetraders.io/my/account"
MY_LOANS = "https://api.spacetraders.io/my/loans"
MY_SHIPS = "https://api.spacetraders.io/my/ships"
MY_STRUCTURES = "https://api.spacetraders.io/my/structures"

proxy_workaround = {"proxies": {"http": None, "https": None}}
# proxy_workaround = {"proxies": {"https": "http://127.0.0.1:8080"}, "verify": False}

###
# summary tab
#

trader_name = None
trader_token = None
widgets = {}


def refresh_user_summary(*args):
    try:
        response = requests.get(
            MY_ACCOUNT, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            # print(result)

            widgets["user_joined"].set(util.format_datetime(result["user"]["joinedAt"]))
            widgets["user_worth"].set(f"{result['user']['credits']:n}")

        response = requests.get(
            MY_LOANS, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            # print(result)
            widgets["loan_view"].delete(*widgets["loan_view"].get_children())
            for row in result["loans"]:
                widgets["loan_view"].insert(
                    "",
                    "end",
                    text="loan_values",
                    values=(
                        row["type"],
                        row["status"],
                        util.format_datetime(row["due"]),
                        f"{row['repaymentAmount']:n}",
                    ),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

        response = requests.get(
            MY_SHIPS, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            # print(result)
            widgets["ship_view"].delete(*widgets["ship_view"].get_children())
            for row in result["ships"]:
                widgets["ship_view"].insert(
                    "",
                    "end",
                    text="ship_values",
                    values=(
                        row["manufacturer"],
                        row["class"],
                        row["type"],
                        row["location"] if "location" in row else "In transit",
                    ),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

        response = requests.get(
            MY_STRUCTURES, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            # print(result)
            widgets["structure_view"].delete(*widgets["structure_view"].get_children())

            for row in result["structures"]:
                widgets["structure_view"].insert(
                    "",
                    "end",
                    text="structure_values",
                    values=(row["type"], row["location"], row["active"], row["status"]),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)


def create_summary_tab(parent, login_name, login_token, logout_method):
    global trader_name, trader_token
    trader_name = login_name
    trader_token = login_token

    user_summary = ttk.LabelFrame(parent, text="Trader", relief="groove", padding=5)

    user_joined = tk.StringVar()
    user_worth = tk.StringVar()

    widgets["user_joined"] = user_joined
    widgets["user_worth"] = user_worth

    ttk.Label(user_summary, textvariable=trader_name, anchor=tk.CENTER).grid(
        columnspan=2, sticky=tk.EW
    )
    ttk.Label(user_summary, text="Joined on:").grid(row=1, column=0, sticky=tk.W)
    ttk.Label(user_summary, textvariable=user_joined, anchor=tk.CENTER).grid(
        row=1, column=1, sticky=tk.EW
    )
    ttk.Label(user_summary, text="Credits:").grid(row=2, column=0, sticky=tk.W)
    ttk.Label(user_summary, textvariable=user_worth, anchor=tk.CENTER).grid(
        row=2, column=1, sticky=tk.EW
    )
    ttk.Button(user_summary, text="Logout", command=logout_method).grid(
        row=3, column=0, columnspan=2, sticky=tk.EW
    )

    user_summary.columnconfigure(0, weight=1)

    loan_summary = ttk.LabelFrame(parent, text="Loans", relief="groove", padding=5)
    loan_view = ttk.Treeview(
        loan_summary,
        height=3,
        columns=("Type", "Status", "Due", "Amount"),
        show="headings",
    )
    loan_view.column("Type", anchor=tk.W, width=20)
    loan_view.column("Status", anchor=tk.W, width=20)
    loan_view.column("Due", anchor=tk.W, width=20)
    loan_view.column("Amount", anchor=tk.E, width=30)
    loan_view.heading("Type", text="Type")
    loan_view.heading("Status", text="Status")
    loan_view.heading("Due", text="Due")
    loan_view.heading("Amount", text="Amount Owing")
    loan_view.grid(sticky=tk.NSEW)
    loan_scroll = ttk.Scrollbar(
        loan_summary, orient=tk.VERTICAL, command=loan_view.yview
    )
    loan_scroll.grid(column=1, row=0, sticky=tk.NS)
    loan_view["yscrollcommand"] = loan_scroll.set

    loan_summary.columnconfigure(0, weight=1)
    loan_summary.rowconfigure(0, weight=1)

    ship_summary = ttk.LabelFrame(parent, text="Ships", relief="groove", padding=5)
    ship_view = ttk.Treeview(
        ship_summary,
        height=3,
        columns=("Manufacturer", "Class", "Type", "Location"),
        show="headings",
    )
    ship_view.column("Manufacturer", anchor=tk.W, width=30)
    ship_view.column("Class", anchor=tk.W, width=30)
    ship_view.column("Type", anchor=tk.W, width=30)
    ship_view.column("Location", anchor=tk.W, width=30)
    ship_view.heading("Manufacturer", text="Manufacturer")
    ship_view.heading("Class", text="Class")
    ship_view.heading("Type", text="Type")
    ship_view.heading("Location", text="Location")
    ship_view.grid(sticky=tk.NSEW)
    ship_scroll = ttk.Scrollbar(
        ship_summary, orient=tk.VERTICAL, command=ship_view.yview
    )
    ship_scroll.grid(column=1, row=0, sticky=tk.NS)
    ship_view["yscrollcommand"] = ship_scroll.set

    ship_summary.columnconfigure(0, weight=1)
    ship_summary.rowconfigure(0, weight=1)

    structure_summary = ttk.LabelFrame(
        parent, text="Structures", relief="groove", padding=5
    )
    structure_view = ttk.Treeview(
        structure_summary,
        height=3,
        columns=("Type", "Location", "Active", "Status"),
        show="headings",
    )
    structure_view.column("Type", anchor=tk.W, width=20)
    structure_view.column("Location", anchor=tk.W, width=20)
    structure_view.column("Active", anchor=tk.W, width=20)
    structure_view.column("Status", anchor=tk.W, width=60)
    structure_view.heading("Type", text="Type")
    structure_view.heading("Location", text="Location")
    structure_view.heading("Active", text="Active")
    structure_view.heading("Status", text="Status")
    structure_view.grid(sticky=tk.NSEW)
    structure_scroll = ttk.Scrollbar(
        structure_summary, orient=tk.VERTICAL, command=structure_view.yview
    )
    structure_scroll.grid(column=1, row=0, sticky=tk.NS)
    structure_view["yscrollcommand"] = structure_scroll.set

    structure_summary.columnconfigure(0, weight=1)
    structure_summary.rowconfigure(0, weight=1)

    user_summary.grid(row=0, column=0, sticky=tk.NSEW)
    loan_summary.grid(row=0, column=1, sticky=tk.NSEW)
    ship_summary.grid(row=1, column=0, sticky=tk.NSEW)
    structure_summary.grid(row=1, column=1, sticky=tk.NSEW)

    parent.columnconfigure(0, weight=1)
    parent.columnconfigure(1, weight=1)
    parent.rowconfigure(0, weight=1)
    parent.rowconfigure(1, weight=1)

    widgets["loan_view"] = loan_view
    widgets["ship_view"] = ship_view
    widgets["structure_view"] = structure_view
