import tkinter as tk
from tkinter import ttk

from datetime import datetime, timezone

import json
import os.path
import requests

TRADER_FILE = "traders.json"

CLAIM_USER = 'f"https://api.spacetraders.io/users/{username}/claim"'
MY_ACCOUNT = "https://api.spacetraders.io/my/account"

proxy_workaround = {"proxies": {"http": None, "https": None}}
# proxy_workaround = {"proxies": {"https": "http://127.0.0.1:8080"}, "verify": False}

###
# user registration/login tab
#

widgets = {}
success_method = None


def load_trader_logins():
    known_traders = {}

    if os.path.exists(TRADER_FILE):
        with open(TRADER_FILE) as json_traders:
            known_traders = json.load(json_traders)

    return known_traders


def store_trader_login(json_result):
    known_traders = load_trader_logins()
    known_traders[json_result["user"]["username"]] = json_result["token"]

    with open(TRADER_FILE, "w") as json_traders:
        json.dump(known_traders, json_traders)


def generate_login_combobox():
    known_traders = load_trader_logins()
    trader_list = sorted(known_traders.keys(), key=str.casefold)

    widgets["id_login"]["values"] = trader_list


def register_trader():
    username = widgets["trader_name"].get()  # noqa: F841
    claim_url = eval(CLAIM_USER)  # username from above used here

    try:
        response = requests.post(claim_url, **proxy_workaround)
        if response.status_code < 400:
            result = response.json()
            result["user"]["joinedAt"] = datetime.now(timezone.utc).isoformat()
            store_trader_login(result)
            success_method(result)
            widgets["trader_name"].set("")
        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)


def login_trader():
    widgets["trader_token"].set(widgets["trader_login"].get())

    # -1 -> user entered a new token, so there won't be a name selected
    if widgets["id_login"].current() != -1:
        known_traders = load_trader_logins()
        widgets["trader_token"].set(known_traders[widgets["trader_login"].get()])

    try:
        response = requests.get(
            MY_ACCOUNT,
            params={"token": widgets["trader_token"].get()},
            **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            result["token"] = widgets[
                "trader_token"
            ].get()  # used to hold the token for later
            success_method(result)
            # print(result)

            # -1, so now store the trader name / token for future runs
            if widgets["id_login"].current() == -1:
                store_trader_login(result)

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)


def create_registration_login_tab(parent, login_success):
    global success_method
    success_method = login_success

    trader_name = tk.StringVar()
    trader_login = tk.StringVar()
    trader_token = (
        tk.StringVar()
    )  # going to use this to remember the currently logged in trader

    widgets["trader_name"] = trader_name
    widgets["trader_login"] = trader_login
    widgets["trader_token"] = trader_token

    # left hand frame will check/register new users and return/store the UUID
    register = ttk.LabelFrame(parent, text="Register", relief="groove", padding=5)
    register.grid(sticky=tk.NSEW)

    # widgets required on the left are a label, an entry, and a button
    ttk.Label(
        register,
        text="Enter a new trader name\nto start a new account",
        anchor=tk.CENTER,
    ).grid(sticky=tk.EW)
    username = ttk.Entry(register, textvariable=trader_name)
    username.grid(row=1, column=0, sticky=tk.EW)
    ttk.Button(register, text="Register new trader", command=register_trader).grid(
        row=2, column=0, columnspan=2, sticky=tk.EW
    )

    register.columnconfigure(0, weight=1)
    register.rowconfigure(0, weight=1)

    ttk.Label(parent, text="or", padding=10, anchor=tk.CENTER).grid(
        row=0, column=1, sticky=tk.EW
    )

    # right hand frame will allow to choose from known users and/or paste in existing
    # UUID to login and play as that user
    login = ttk.LabelFrame(parent, text="Login", relief="groove", padding=5)
    login.grid(row=0, column=2, sticky=tk.NSEW)

    # widgets required on the right are a dropdown, and a button
    ttk.Label(
        login,
        text="Choose the trader to play as\nor paste an existing id",
        anchor=tk.CENTER,
    ).grid(sticky=tk.EW)
    id_login = ttk.Combobox(
        login, textvariable=trader_login, postcommand=generate_login_combobox
    )
    id_login.grid(row=1, column=0, sticky=tk.EW)
    ttk.Button(login, text="Login trader", command=login_trader).grid(
        row=2, column=0, columnspan=2, sticky=tk.EW
    )

    widgets["id_login"] = id_login

    login.columnconfigure(0, weight=1)
    login.rowconfigure(0, weight=1)

    parent.columnconfigure(0, weight=1)
    parent.columnconfigure(2, weight=1)
    parent.rowconfigure(0, weight=1)

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
