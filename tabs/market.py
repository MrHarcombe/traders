import tkinter as tk
from tkinter import ttk

import requests

MY_SHIPS = "https://api.spacetraders.io/my/ships"
CURRENT_MARKET = 'f"https://api.spacetraders.io/locations/{current_planet}/marketplace"'

proxy_workaround = {"proxies": {"http": None, "https": None}}
# proxy_workaround = {"proxies": {"https": "http://127.0.0.1:8080"}, "verify": False}

###
# leaderboard tab
#

trader_token = None
widgets = {}


def refresh_marketplace(*args):
    try:
        current_planet = requests.get(
            MY_SHIPS, params={"token": trader_token.get()}, **proxy_workaround
        ).json()["ships"][0]["location"]
        print(current_planet)
        current_market = eval(CURRENT_MARKET)
        response = requests.get(
            current_market, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()

            # print(result)
            widgets["market_view"].delete(*widgets["market_view"].get_children())
            widgets["market_view"].heading("#1", text="Item")
            widgets["market_view"].column("#1", minwidth=100)

            widgets["market_view"].heading("#2", text="Quantity")
            widgets["market_view"].column("#1", minwidth=250)

            widgets["market_view"].heading("#3", text="Buy Price")
            widgets["market_view"].column("#1", minwidth=100)

            widgets["market_view"].heading("#4", text="Sell Price")
            widgets["market_view"].column("#1", minwidth=100)

            # print(result.ship)
            for row in result["marketplace"]:
                # print(row)
                widgets["market_view"].insert(
                    "",
                    "end",
                    text="values",
                    values=(
                        row["symbol"],
                        row["quantityAvailable"],
                        row["purchasePricePerUnit"],
                        row["sellPricePerUnit"],
                    ),
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)


def refresh_location(parent, login_token):
    result = "Couldn't fetch location!"
    ttk.Button(parent, text="Refresh!", command=refresh_location, state=tk.NORMAL).grid(
        row=2, column=0, columnspan=2, sticky=tk.EW
    )
    try:
        response = requests.get(
            MY_SHIPS, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()["ships"][0]["location"]
            widgets["current_location"].set("Planet:\n" + result)
            ttk.Button(
                parent, text="Refresh!", command=refresh_location, state=tk.DISABLED
            ).grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        else:

            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        widgets["current_location"].set(result)
        # ttk.Button(planet,text="Refresh!", command=refresh_location,state=NORMAL).grid(row=2, column=0, columnspan=2, sticky=EW)

        print("Failed:", ce)


def create_market_tab(parent, login_token):
    global trader_token
    trader_token = login_token
    current_location = tk.StringVar()
    widgets["current_location"] = current_location

    market_frame = ttk.Frame(parent)
    market_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
    market_LF = ttk.LabelFrame(
        market_frame, text="Current Location", relief="groove", padding=5
    )
    market_LF.grid(sticky=tk.NSEW)
    current_location = ttk.Label(
        market_LF, text="Planet:", textvariable=current_location, anchor=tk.CENTER
    ).grid(sticky=tk.EW)

    market_LF.columnconfigure(0, weight=1)
    market_LF.rowconfigure(0, weight=1)

    market_frame.columnconfigure(0, weight=1)
    market_frame.columnconfigure(2, weight=1)
    market_frame.rowconfigure(0, weight=1)

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)

    # - Market Place

    market_view = ttk.Treeview(
        parent,
        height=6,
        columns=("Item", "Quantity", "Buy Price", "Sell Price"),
        show="headings",
    )

    widgets["market_view"] = market_view

    market_view.column("Item", anchor=tk.CENTER, width=100)
    market_view.column("Quantity", anchor=tk.CENTER, width=100)
    market_view.column("Buy Price", anchor=tk.CENTER, width=75)
    market_view.column("Sell Price", anchor=tk.CENTER, width=75)
    market_view.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)
    market_scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=market_view.yview)
    market_scroll.grid(row=0, column=4, sticky=tk.NSEW)
    market_view["yscrollcommand"] = market_scroll.set

    market_view.columnconfigure(0, weight=1)
    market_view.rowconfigure(0, weight=1)
