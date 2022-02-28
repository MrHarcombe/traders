from tkinter import *
from tkinter import ttk

import json
import os.path
import requests

TRADER_FILE = 'traders.json'

CLAIM_USER = 'f"https://api.spacetraders.io/users/{username}/claim"'
MY_ACCOUNT = 'https://api.spacetraders.io/my/account'
CURRENT_LEADERBOARD = 'https://api.spacetraders.io/game/leaderboard/net-worth'
MY_LOANS = 'https://api.spacetraders.io/my/loans'
MY_SHIPS = 'https://api.spacetraders.io/my/ships'
MY_STRUCTURES = 'https://api.spacetraders.io/my/structures'


def load_trader_logins():
    known_traders = {}

    if os.path.exists(TRADER_FILE):
        with open(TRADER_FILE) as json_traders:
            known_traders = json.load(json_traders)

    return known_traders


def store_trader_login(json_result):
    known_traders = load_trader_logins()
    known_traders[json_result['user']['username']] = json_result['token']

    with open(TRADER_FILE, 'w') as json_traders:
        json.dump(known_traders, json_traders)


def generate_login_combobox():
    known_traders = load_trader_logins()
    trader_list = sorted(known_traders.keys(), key=str.casefold)

    return trader_list


def show_trader_summary(json_result):
    tabs.tab(0, state=DISABLED)
    tabs.tab(1, state=NORMAL)
    tabs.tab(2, state=NORMAL)
    
    trader_login.set(json_result['user']['username'])
    trader_token.set(json_result['token'])
    
    tabs.select(1)


def register_trader():
    username = trader_name.get()
    claim_url = eval(CLAIM_USER)
    try:
        response = requests.post(claim_url)
        if response.status_code < 400:
            result = response.json()
            store_trader_login(result)
        else:
            print('Failed:', response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print('Failed:', ce)


def login_trader():
    trader_token.set(trader_login.get())

    # -1 -> user entered a new token
    if id_login.current() != -1:
        known_traders = load_trader_logins()
        trader_token.set(known_traders[trader_login.get()])

    try:
        response = requests.get(MY_ACCOUNT, params={'token': trader_token.get()})
        if response.status_code == 200:
            result = response.json()
            result['token'] = trader_token.get() # used to hold the token for later
            show_trader_summary(result)
            # print(result)

            # -1, so now store the trader name / token for future runs
            if id_login.current() == -1:
                store_trader_login(result)

        else:
            print('Failed:', response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print('Failed:', ce)


def logout_trader():
    tabs.tab(0, state=NORMAL)
    tabs.tab(1, state=DISABLED)
    tabs.tab(2, state=DISABLED)
    
    trader_login.set('')
    trader_token.set('')
    
    tabs.select(0)


def refresh_tabs(event):
    selected_index = tabs.index(tabs.select())
    if selected_index == 1:
        refresh_user_summary()
        
    elif selected_index == 2:
        refresh_leaderboard()


def refresh_user_summary(*args):
    try:
        response = requests.get(MY_LOANS, params={'token': trader_token.get()})
        if response.status_code == 200:
            result = response.json()
            # print(result)
            loan_view.delete(*loan_view.get_children())
            loan_view.heading('#1', text='Type')
            loan_view.heading('#2', text='Status')
            loan_view.heading('#3', text='Due')
            loan_view.heading('#4', text='Amount Owing')
            for row in result['loans']:
                loan_view.insert('', 'end', text='loan_values', values=(row['type'], row['status'], row['due'], row['repaymentAmount']))

        else:
            print('Failed:', response.status_code, response.reason, response.text)

        response = requests.get(MY_SHIPS, params={'token': trader_token.get()})
        if response.status_code == 200:
            result = response.json()
            # print(result)
            ship_view.delete(*ship_view.get_children())
            ship_view.heading('#1', text='Manufacturer')
            ship_view.heading('#2', text='Class')
            ship_view.heading('#3', text='Type')
            ship_view.heading('#4', text='Location')
            for row in result['ships']:
                ship_view.insert('', 'end', text='ship_values', values=(row['manufacturer'], row['class'], row['type'], row['location'] if 'location' in row else 'In transit'))

        else:
            print('Failed:', response.status_code, response.reason, response.text)

        response = requests.get(MY_STRUCTURES, params={'token': trader_token.get()})
        if response.status_code == 200:
            result = response.json()
            # print(result)
            structure_view.delete(*structure_view.get_children())
            structure_view.heading('#1', text='Type')
            structure_view.heading('#2', text='Location')
            structure_view.heading('#3', text='Active')
            structure_view.heading('#4', text='Status')
            for row in result['structures']:
                structure_view.insert('', 'end', text='structure_values', values=(row['type'], row['location'], row['active'], row['status']))

        else:
            print('Failed:', response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print('Failed:', ce)


def refresh_leaderboard(*args):
    try:
        response = requests.get(CURRENT_LEADERBOARD, params={'token': trader_token.get()})
        if response.status_code == 200:
            result = response.json()
            
            # print(result)
            leaderboard_view.delete(*leaderboard_view.get_children())
            leaderboard_view.heading('#1', text='Rank')
            leaderboard_view.heading('#2', text='Trader')
            leaderboard_view.heading('#3', text='Net Worth')
            for row in result['netWorth']:
                leaderboard_view.insert('', 'end', text='values', values=(row['rank'], row['username'], row['netWorth']))

        else:
            print('Failed:', response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print('Failed:', ce)


###
# Root window, with app title
#
root = Tk()
root.title("Io Space Trading")

# Main themed frame, for all other widgets to rest upon
main = ttk.Frame(root, padding='3 3 12 12')
main.grid(sticky=NSEW)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Tabbed widget for rest of the app to run in
tabs = ttk.Notebook(main)
tabs.grid(sticky=NSEW)
tabs.bind('<<NotebookTabChanged>>', refresh_tabs)

main.columnconfigure(0, weight=1)
main.rowconfigure(0, weight=1)

# setup the three main tabs
user = ttk.Frame(tabs)
summary = ttk.Frame(tabs)
leaderboard = ttk.Frame(tabs)

tabs.add(user, text='User')
tabs.add(summary, text='Summary')
tabs.add(leaderboard, text='Leaderboard')

tabs.tab(1, state=DISABLED)
tabs.tab(2, state=DISABLED)

###
# user registration/login tab
#

user_frame = ttk.Frame(user)
user_frame.grid(row=0, column=0, columnspan=2, sticky=NSEW)

# left hand frame will check/register new users and return/store the UUID
register = ttk.LabelFrame(user_frame, text='Register', relief='groove', padding=5)
register.grid(sticky=NSEW)

# widgets required on the left are a label, an entry, and a button
trader_name = StringVar()
ttk.Label(register, text='Enter a new trader name\nto start a new account', anchor=CENTER).grid(sticky=EW)
username = ttk.Entry(register, textvariable=trader_name)
username.grid(row=1, column=0, sticky=EW)
ttk.Button(register, text='Register new trader', command=register_trader).grid(row=2, column=0, columnspan=2, sticky=EW)

register.columnconfigure(0, weight=1)
register.rowconfigure(0, weight=1)

ttk.Label(user_frame, text='or', padding=10, anchor=CENTER).grid(row=0, column=1, sticky=EW)

# right hand frame will allow to choose from known users and/or paste in existing
# UUID to login and play as that user
login = ttk.LabelFrame(user_frame, text='Login', relief='groove', padding=5)
login.grid(row=0, column=2, sticky=NSEW)

# widgets required on the right are a dropdown, and a button
trader_login = StringVar()
trader_token = StringVar() # going to use this to remember the currently logged in trader
ttk.Label(login, text='Choose the trader to play as\nor paste an existing id').grid(sticky=EW)
id_login = ttk.Combobox(login, textvariable=trader_login, values=generate_login_combobox())
id_login.grid(row=1, column=0, sticky=EW)
ttk.Button(login, text='Login trader', command=login_trader).grid(row=2, column=0, columnspan=2, sticky=EW)

login.columnconfigure(0, weight=1)
login.rowconfigure(0, weight=1)

user_frame.columnconfigure(0, weight=1)
user_frame.columnconfigure(2, weight=1)
user_frame.rowconfigure(0, weight=1)

user.columnconfigure(0, weight=1)
user.rowconfigure(0, weight=1)

###
# summary tab
#

user_summary = ttk.LabelFrame(summary, text='Trader', relief='groove', padding=5)
ttk.Label(user_summary, textvariable=trader_login, anchor=CENTER).grid(sticky=NSEW)
ttk.Button(user_summary, text='Logout', command=logout_trader).grid(row=1, column=0, sticky=EW)

user_summary.columnconfigure(0, weight=1)

loan_summary = ttk.LabelFrame(summary, text='Loans', relief='groove', padding=5)
loan_view = ttk.Treeview(loan_summary, height=3, columns=('Type', 'Status', 'Due', 'Amount'), show='headings')
loan_view.column('Type', anchor=W, width=20)
loan_view.column('Status', anchor=W, width=20)
loan_view.column('Due', anchor=W, width=20)
loan_view.column('Amount', anchor=E, width=30)
loan_view.grid(sticky=NSEW)
loan_scroll = ttk.Scrollbar(loan_summary, orient=VERTICAL, command=loan_view.yview)
loan_scroll.grid(column=1, row=0, sticky=NS)
loan_view['yscrollcommand'] = loan_scroll.set

loan_summary.columnconfigure(0, weight=1)
loan_summary.rowconfigure(0, weight=1)

ship_summary = ttk.LabelFrame(summary, text='Ships', relief='groove', padding=5)
ship_view = ttk.Treeview(ship_summary, height=3, columns=('Manufacturer', 'Class', 'Type', 'Location'), show='headings')
ship_view.column('Manufacturer', anchor=W, width=30)
ship_view.column('Class', anchor=W, width=30)
ship_view.column('Type', anchor=W, width=30)
ship_view.column('Location', anchor=W, width=30)
ship_view.grid(sticky=NSEW)
ship_scroll = ttk.Scrollbar(ship_summary, orient=VERTICAL, command=ship_view.yview)
ship_scroll.grid(column=1, row=0, sticky=NS)
ship_view['yscrollcommand'] = ship_scroll.set

ship_summary.columnconfigure(0, weight=1)
ship_summary.rowconfigure(0, weight=1)

structure_summary = ttk.LabelFrame(summary, text='Structures', relief='groove', padding=5)
structure_view = ttk.Treeview(structure_summary, height=3, columns=('Type', 'Location', 'Active', 'Status'), show='headings')
structure_view.column('Type', anchor=W, width=20)
structure_view.column('Location', anchor=W, width=20)
structure_view.column('Active', anchor=W, width=20)
structure_view.column('Status', anchor=W, width=60)
structure_view.grid(sticky=NSEW)
structure_scroll = ttk.Scrollbar(structure_summary, orient=VERTICAL, command=structure_view.yview)
structure_scroll.grid(column=1, row=0, sticky=NS)
structure_view['yscrollcommand'] = structure_scroll.set

structure_summary.columnconfigure(0, weight=1)
structure_summary.rowconfigure(0, weight=1)

user_summary.grid(row=0, column=0, sticky=NSEW)
loan_summary.grid(row=0, column=1, sticky=NSEW)
ship_summary.grid(row=1, column=0, sticky=NSEW)
structure_summary.grid(row=1, column=1, sticky=NSEW)

summary.columnconfigure(0, weight=1)
summary.columnconfigure(1, weight=1)
summary.rowconfigure(0, weight=1)
summary.rowconfigure(1, weight=1)

###
# leaderboard tab
#

leaderboard_view = ttk.Treeview(leaderboard, height=6, columns=('Rank', 'Trader', 'Net Worth'), show='headings')
leaderboard_view.column('Rank', anchor=CENTER, width=10)
leaderboard_view.column('Trader', anchor=W, width=100)
leaderboard_view.column('Net Worth', anchor=E, width=100)
leaderboard_view.grid(sticky=NSEW)
leaderboard_scroll = ttk.Scrollbar(leaderboard, orient=VERTICAL, command=leaderboard_view.yview)
leaderboard_scroll.grid(column=1, row=0, sticky=NS)
leaderboard_view['yscrollcommand'] = leaderboard_scroll.set
refresh = ttk.Button(leaderboard, text='Refresh', command=refresh_leaderboard)
refresh.grid(column=0, row=1, sticky=EW)

leaderboard.columnconfigure(0, weight=1)
leaderboard.rowconfigure(0, weight=1)

root.mainloop()
