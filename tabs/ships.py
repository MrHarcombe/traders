from threading import local
import tkinter as tk
from tkinter import ttk
import requests
import util
import tkinter.messagebox

GETships = "https://api.spacetraders.io/systems/OE/ship-listings"
MY_SHIPS = "https://api.spacetraders.io/my/ships"
ACCOUNT = "https://api.spacetraders.io/my/account"

widgets = {}
trader_token = None
parent = None

proxy_workaround = {"proxies": {"http": None, "https": None}}

purchaseLocations = {'test':[]}


def create_ships_tab(parentWidget, login_token):
    global trader_token
    trader_token = login_token

    global parent
    parent = parentWidget

    ships_page = ttk.LabelFrame(parent, text='Available Ships', relief='groove', padding=5)

    ships_page.columnconfigure(0, weight=1)
    ships_page.rowconfigure(0, weight=1)
    widgets['LeftFrame'] = ships_page

    #All ships table

    ships_view = ttk.Treeview(ships_page, height=3, columns=(1, 2, 3, 4, 5, 6, 7), show='headings')
    ships_view.heading(1, text='Class')
    ships_view.heading(2, text='Manafacturer')
    ships_view.heading(3, text='Cargo')
    ships_view.heading(4, text='Plating')
    ships_view.heading(5, text='Speed')
    ships_view.heading(6, text='Type')
    ships_view.heading(7, text='Weapons')
    ships_view.column(1, anchor=tk.W, width=40)
    ships_view.column(2, anchor=tk.W, width=90)
    ships_view.column(3, anchor=tk.W, width=40)
    ships_view.column(4, anchor=tk.W, width=60)
    ships_view.column(5, anchor=tk.W, width=60)
    ships_view.column(6, anchor=tk.W, width=40)
    ships_view.column(7, anchor=tk.W, width=40)

    widgets['ShipsTable'] = ships_view

    ships_view.grid(row=0, sticky=(tk.NSEW))
    ships_scrolly = ttk.Scrollbar(ships_page, orient=tk.VERTICAL, command=ships_view.yview)
    ships_scrolly.grid(column=1, row=0, sticky=(tk.N,tk.S))
    ships_view['yscrollcommand'] = ships_scrolly.set

    #Current Ships table

    ship_summary = ttk.LabelFrame(parent, text=" Current Ships", relief="groove", padding=5)
    ship_view = ttk.Treeview(
        ship_summary,
        height=3,
        columns=("Manufacturer", "Class", "Type", "Location"),
        show="headings",
    )
    ship_view.column("Manufacturer", anchor=tk.W, width=90)
    ship_view.column("Class", anchor=tk.W, width=40)
    ship_view.column("Type", anchor=tk.W, width=40)
    ship_view.column("Location", anchor=tk.W, width=60)
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

    widgets['CurrentShips'] = ship_view

    #Drop down menu

    variable = tk.StringVar(parent)
    variable.set("Double click row to select ship in table") # default value

    dropDown = ttk.OptionMenu(ships_page, variable)
    dropDown.option_clear
    dropDown.grid(row=1, sticky=(tk.NSEW),padx=20,pady=20)

    widgets['Dropdown'] = dropDown

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(1, weight=1)
    parent.rowconfigure(1, weight=1)

    ships_page.grid(row=0, column=0, sticky=tk.NSEW)
    ship_summary.grid(row=0, column=1, sticky=tk.NSEW)

    #credits refresh
    global creditsCurrent
    creditsCurrent = tk.StringVar(parent)
    try:
        response = requests.get(
            ACCOUNT, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            creditsCurrent.set(result['user']['credits'])
    except ConnectionError as ce:
        print("Failed:", ce)

    label = ttk.Label(ships_page, text=creditsCurrent.get())
    widgets['CreditsLabel'] = label
    label.grid(row=2, column=0, sticky=tk.NSEW)



def purchaseMenu(event):
    data = event.split(":")

    try:
        response = requests.get(
            ACCOUNT, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            credits = result['user']['credits']
            if credits < int(data[1][1:]):
                tkinter.messagebox.showerror(title='Insufficient Credits',message='You do not have enough credits to purchase this ship')
            else:
                try:
                    response = requests.get(
                    MY_SHIPS, params={"token": trader_token.get()}, **proxy_workaround
                    )
                    if response.status_code == 200:
                        result = response.json()
                        locationAccepted = 0
                        for ship in result['ships']:
                            if ship['location'] == data[0]:
                                locationAccepted = 1
                                selected = widgets['ShipsTable'].selection()[0]
                                shipType = widgets['ShipsTable'].item(selected,"values")[5]
                                print(trader_token.get(),ship['location'],shipType)
                                if tkinter.messagebox.askyesno(title='Confirm Purchase',message='Do you want to purchase %s for %s credits'%(shipType,int(data[1][1:]))):
                                    try:
                                        response = requests.get(
                                            MY_SHIPS, params={"token": trader_token.get(),'location':ship['location'],'type':shipType}, **proxy_workaround
                                        )
                                        if response.status_code == 200:
                                            result = response.json()
                                            shipID = ship['id']
                                            print(shipID)
                                    except ConnectionError as ce:
                                        print("Failed:", ce)
                                break
                        if locationAccepted == 0:
                            tkinter.messagebox.showerror(title='Location Error',message='No ships at purchase locations')
                except ConnectionError as ce:
                    print("Failed:", ce)
    except ConnectionError as ce:
        print("Failed:", ce)


#cl6z26nre62422515s6z04x7nsv


def refresh_ships():
    try:
        response = requests.get(
            GETships, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            for ship in result['shipListings']:
                widgets['ShipsTable'].insert(
                    "",
                    "end",
                    text="ship_values",
                    values=(
                        ship['class'],
                        ship['manufacturer'],
                        ship['maxCargo'],
                        ship['plating'],
                        ship['speed'],
                        ship['type'],
                        ship['weapons']
                        )
                )
                locations = []
                for location in ship['purchaseLocations']:
                    l = "%s: %s"%(location['location'],location['price'])
                    locations.append(l)

                purchaseLocations[ship['type']] = locations


            #print(result)
            widgets['ShipsTable'].bind('<Double-1>',update_location_select)

        else:
            print("Failed:", response.status_code, response.reason, response.text)

    except ConnectionError as ce:
        print("Failed:", ce)

    

    #credits refresh
    try:
        response = requests.get(
            ACCOUNT, params={"token": trader_token.get()}, **proxy_workaround
        )
        if response.status_code == 200:
            result = response.json()
            creditsCurrent.set("Credits: "+str(result['user']['credits']))
    except ConnectionError as ce:
        print("Failed:", ce)

    widgets["CreditsLabel"]['text'] = creditsCurrent.get()

    

    

def refresh_shipSummary():
    response = requests.get(
        MY_SHIPS, params={"token": trader_token.get()}, **proxy_workaround
    )
    if response.status_code == 200:
        result = response.json()
        # print(result)
        widgets["CurrentShips"].delete(*widgets["CurrentShips"].get_children())
        for row in result["ships"]:
            widgets["CurrentShips"].insert(
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


def update_location_select(event):
    selected = widgets['ShipsTable'].selection()[0]
    dropdownData = purchaseLocations[widgets['ShipsTable'].item(selected,"values")[5]] #finds price and location in dictionary using type as key
    widgets['Dropdown'].grid_forget()
    del widgets['Dropdown']

    variable = tk.StringVar(parent)

    options = ["Select location to purchase from"]
    for item in dropdownData:
        options.append(item)

    variable.set(options[0])

    dropDown = ttk.OptionMenu(widgets['LeftFrame'], variable,*options, command=purchaseMenu)
    dropDown.grid(row=1, sticky=tk.NSEW,padx=20,pady=20)

    widgets['Dropdown'] = dropDown

