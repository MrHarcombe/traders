import tkinter as tk
from tkinter import ttk

import locale

from tabs import leaderboard, login, summary, market, loans
import util

locale.setlocale(locale.LC_ALL, "")  # Use '' for auto, or force e.g. to 'en_US.UTF-8'


def login_trader(json_result):
    tabs.tab(0, state=tk.DISABLED)
    tabs.tab(1, state=tk.NORMAL)
    tabs.tab(2, state=tk.NORMAL)
    tabs.tab(3, state=tk.NORMAL)
    tabs.tab(4, state=tk.NORMAL)

    login.widgets["trader_login"].set(json_result["user"]["username"])
    login.widgets["trader_token"].set(json_result["token"])

    summary.widgets["user_joined"].set(
        util.format_datetime(json_result["user"]["joinedAt"])
    )
    summary.widgets["user_worth"].set(f"{json_result['user']['credits']:n}")

    tabs.select(1)


def logout_trader():
    tabs.tab(0, state=tk.NORMAL)
    tabs.tab(1, state=tk.DISABLED)
    tabs.tab(2, state=tk.DISABLED)
    tabs.tab(3, state=tk.DISABLED)
    tabs.tab(4, state=tk.DISABLED)

    login.widgets["trader_login"].set("")
    login.widgets["trader_token"].set("")

    tabs.select(0)


def refresh_tabs(event):
    selected_index = tabs.index(tabs.select())
    if selected_index == 1:
        summary.refresh_user_summary()

    elif selected_index == 2:
        leaderboard.refresh_leaderboard()
    elif selected_index == 3:
        market.refresh_marketplace()
        market.refresh_location(market_tab, login.widgets["trader_token"])
    elif selected_index == 4:
        loans.refresh_loans()


###
# Root window, with app title
#
root = tk.Tk()
root.title("Io Space Trading")

# Main themed frame, for all other widgets to rest upon
main = ttk.Frame(root, padding=3)
main.grid(sticky=tk.NSEW)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Tabbed widget for rest of the app to run in
tabs = ttk.Notebook(main)
tabs.grid(sticky=tk.NSEW)
tabs.bind("<<NotebookTabChanged>>", refresh_tabs)

main.columnconfigure(0, weight=1)
main.rowconfigure(0, weight=1)

# setup the three main tabs
login_tab = ttk.Frame(tabs, padding="3 1 6 5")
summary_tab = ttk.Frame(tabs, padding="3 1 6 5")
leaderboard_tab = ttk.Frame(tabs, padding="3 1 6 5")
market_tab = ttk.Frame(tabs, padding="3 1 6 5")
loans_tab = ttk.Frame(tabs, padding="3 1 6 5")

tabs.add(login_tab, text="Login")
tabs.add(summary_tab, text="Summary")
tabs.add(leaderboard_tab, text="Leaderboard")
tabs.add(market_tab, text="Market")
tabs.add(loans_tab, text="Loans")

tabs.tab(1, state=tk.DISABLED)
tabs.tab(2, state=tk.DISABLED)
tabs.tab(3, state=tk.DISABLED)
tabs.tab(4, state=tk.DISABLED)

login.create_registration_login_tab(login_tab, login_trader)
summary.create_summary_tab(
    summary_tab,
    login.widgets["trader_login"],
    login.widgets["trader_token"],
    logout_trader,
)
leaderboard.create_leaderboard_tab(leaderboard_tab, login.widgets["trader_token"])
market.create_market_tab(market_tab, login.widgets["trader_token"])
loans.create_loans_tab(loans_tab, login.widgets["trader_token"])

root.mainloop()
