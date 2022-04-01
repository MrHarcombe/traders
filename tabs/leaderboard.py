import tkinter as tk
from tkinter import ttk

import requests

CURRENT_LEADERBOARD = "https://api.spacetraders.io/game/leaderboard/net-worth"

proxy_workaround = {"proxies": {"http": None, "https": None}}
# proxy_workaround = {"proxies": {"https": "http://127.0.0.1:8080"}, "verify": False}

###
# leaderboard tab
#

trader_token = None
widgets = {}


def refresh_leaderboard(*args):
    try:
        response = requests.get(
            CURRENT_LEADERBOARD,
            params={"token": trader_token.get()},
            **proxy_workaround,
        )
        if response.status_code == 200:
            result = response.json()

            # print(result)
            widgets["leaderboard_view"].delete(
                *widgets["leaderboard_view"].get_children()
            )
            for row in result["netWorth"]:
                widgets["leaderboard_view"].insert(
                    "",
                    "end",
                    text="values",
                    values=(row["rank"], row["username"], f"{row['netWorth']:n}"),
                )
            if result["userNetWorth"]["rank"] > 10:
                widgets["leaderboard_view"].insert(
                    "",
                    "end",
                    text="values",
                    values=(
                        result["userNetWorth"]["rank"],
                        result["userNetWorth"]["username"],
                        f"{result['userNetWorth']['netWorth']:n}"
                    )
                )

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)


def create_leaderboard_tab(parent, login_token):
    global trader_token
    trader_token = login_token

    leaderboard_view = ttk.Treeview(
        parent, height=6, columns=("Rank", "Trader", "Net Worth"), show="headings"
    )
    widgets["leaderboard_view"] = leaderboard_view

    leaderboard_view.column("Rank", anchor=tk.CENTER, width=10)
    leaderboard_view.column("Trader", anchor=tk.W, width=100)
    leaderboard_view.column("Net Worth", anchor=tk.E, width=100)
    leaderboard_view.heading("Rank", text="Rank")
    leaderboard_view.heading("Trader", text="Trader")
    leaderboard_view.heading("Net Worth", text="Net Worth")
    leaderboard_view.grid(sticky=tk.NSEW)
    leaderboard_scroll = ttk.Scrollbar(
        parent, orient=tk.VERTICAL, command=leaderboard_view.yview
    )
    leaderboard_scroll.grid(column=1, row=0, sticky=tk.NS)
    leaderboard_view["yscrollcommand"] = leaderboard_scroll.set
    refresh = ttk.Button(parent, text="Refresh", command=refresh_leaderboard)
    refresh.grid(column=0, row=1, sticky=tk.EW)

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
