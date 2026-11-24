''' Soham Mokashi 37
    Sarthak Waghmare 48
    Suhani Chourasia 31'''
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Menu
MENU = {
    'Starters': [
        (1, 'Paneer Tikka', 220, 'food'),
        (2, 'Veg Spring Rolls', 180, 'food'),
        (3, 'Chicken 65', 260, 'food'),
        (4, 'Tomato Soup', 120, 'food')
    ],

    'Main Course': [
        (5, 'Butter Chicken', 340, 'food'),
        (6, 'Paneer Butter Masala', 290, 'food'),
        (7, 'Veg Biryani', 250, 'food'),
        (8, 'Dal Makhani', 230, 'food'),
        (9, 'Butter Naan', 40, 'food')
    ],

    'Desserts': [
        (10, 'Gulab Jamun', 90, 'food'),
        (11, 'Brownie with Ice Cream', 160, 'food'),
        (12, 'Rasmalai', 110, 'food')
    ],

    'Beverages': [
        (13, 'Masala Chai', 40, 'food'),
        (14, 'Fresh Lime Soda', 70, 'food'),
        (15, 'Packaged Water', 30, 'packaged'),
        (16, 'Cola 500ml', 60, 'packaged'),
        (17, 'Packaged Juice', 80, 'packaged')
    ]
}

ITEMS = {}

for category_items in MENU.values():
    for item in category_items:
        ITEMS[item[0]] = item

order = {}

# Database
con = sqlite3.connect('bill_history.db')
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date TEXT,
    subtotal REAL,
    food_gst REAL,
    packaged_gst REAL,
    total REAL,
    people INTEGER
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    item_id INTEGER,
    item_name TEXT,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY(order_id) REFERENCES orders(order_id)
)
''')

cur.execute('PRAGMA table_info(orders)')
existing_columns = [column[1] for column in cur.fetchall()]

if 'subtotal' not in existing_columns:
    cur.execute('ALTER TABLE orders ADD COLUMN subtotal REAL DEFAULT 0')

if 'food_gst' not in existing_columns:
    cur.execute('ALTER TABLE orders ADD COLUMN food_gst REAL DEFAULT 0')

if 'packaged_gst' not in existing_columns:
    cur.execute('ALTER TABLE orders ADD COLUMN packaged_gst REAL DEFAULT 0')

if 'people' not in existing_columns:
    cur.execute('ALTER TABLE orders ADD COLUMN people INTEGER DEFAULT 1')

con.commit()


# Bill Calculation
def get_bill():
    subtotal = 0
    food_total = 0
    packaged_total = 0

    for item_id, quantity in order.items():
        item = ITEMS[item_id]
        amount = item[2] * quantity

        subtotal = subtotal + amount

        if item[3] == 'food':
            food_total = food_total + amount
        else:
            packaged_total = packaged_total + amount

    food_gst = food_total * 0.05
    packaged_gst = packaged_total * 0.18

    total = subtotal + food_gst + packaged_gst

    return subtotal, food_gst, packaged_gst, total


# Display Menu
def show_menu(event=None):
    for row in menu_tree.get_children():
        menu_tree.delete(row)

    category = category_box.get()

    for sr_no, item in enumerate(MENU[category], start=1):
        item_id = item[0]
        name = item[1]
        price = item[2]

        menu_tree.insert(
            '',
            'end',
            values=(sr_no, item_id, name, 'Rs. ' + str(price))
        )


# Add Item
def add_item():
    selected = menu_tree.selection()

    if not selected:
        messagebox.showwarning('Select Item', 'Please select an item.')
        return

    try:
        quantity = int(quantity_box.get())

        if quantity < 1:
            raise ValueError

    except ValueError:
        messagebox.showerror('Invalid Quantity', 'Enter a valid quantity.')
        return

    item_id = int(menu_tree.item(selected[0], 'values')[1])

    if item_id in order:
        order[item_id] = order[item_id] + quantity
    else:
        order[item_id] = quantity

    update_total()


# Remove Item
def remove_item():
    selected = order_tree.selection()

    if not selected:
        messagebox.showwarning('Select Item', 'Select an item to remove.')
        return

    item_id = int(order_tree.item(selected[0], 'values')[1])

    del order[item_id]

    update_total()


# Update Total
def update_total():
    for row in order_tree.get_children():
        order_tree.delete(row)

    sr_no = 1

    for item_id, quantity in order.items():
        item = ITEMS[item_id]

        name = item[1]
        price = item[2]
        amount = price * quantity

        order_tree.insert(
            '',
            'end',
            values=(
                sr_no,
                item_id,
                name,
                quantity,
                'Rs. ' + str(price),
                'Rs. ' + str(amount)
            )
        )

        sr_no = sr_no + 1

    subtotal, food_gst, packaged_gst, total = get_bill()

    subtotal_label.config(
        text='Subtotal: Rs. ' + str(round(subtotal, 2))
    )

    total_label.config(
        text='Final Total: Rs. ' + str(round(total, 2))
    )

    gst_label.config(
        text='Food GST (5%): Rs. ' + str(round(food_gst, 2)) +
        ' | Packaged GST (18%): Rs. ' + str(round(packaged_gst, 2))
    )


# Generate Final Bill
def save_bill():
    if not order:
        messagebox.showwarning('Empty Order', 'Please add items first.')
        return

    try:
        people = int(people_entry.get())

        if people < 1:
            raise ValueError

    except ValueError:
        messagebox.showerror('Invalid Number', 'Enter a valid number of people.')
        return

    subtotal, food_gst, packaged_gst, total = get_bill()

    order_date = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    cur.execute('''
        INSERT INTO orders
        (order_date, subtotal, food_gst, packaged_gst, total, people)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (order_date, subtotal, food_gst, packaged_gst, total, people))

    order_id = cur.lastrowid

    for item_id, quantity in order.items():
        item = ITEMS[item_id]

        cur.execute('''
            INSERT INTO order_items
            (order_id, item_id, item_name, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        ''', (order_id, item_id, item[1], quantity, item[2]))

    con.commit()

    share = round(total / people, 2)

    shares = [share] * people
    shares[-1] = round(total - share * (people - 1), 2)

    invoice = 'ORDER ID: ' + str(order_id)
    invoice = invoice + '\nDate: ' + order_date + '\n\n'

    for item_id, quantity in order.items():
        item = ITEMS[item_id]

        invoice = invoice + item[1] + ' x ' + str(quantity)
        invoice = invoice + ' = Rs. ' + str(round(item[2] * quantity, 2))
        invoice = invoice + '\n'

    invoice = invoice + '\nSubtotal: Rs. ' + str(round(subtotal, 2))
    invoice = invoice + '\nFood GST (5%): Rs. ' + str(round(food_gst, 2))
    invoice = invoice + '\nPackaged GST (18%): Rs. ' + str(round(packaged_gst, 2))
    invoice = invoice + '\nFINAL BILL: Rs. ' + str(round(total, 2))
    invoice = invoice + '\n\nSplit between ' + str(people) + ' people:\n'

    for number, amount in enumerate(shares, start=1):
        invoice = invoice + '\nPerson ' + str(number)
        invoice = invoice + ': Rs. ' + str(amount)

    messagebox.showinfo('Final Bill', invoice)

    order.clear()
    update_total()

    people_entry.delete(0, tk.END)
    people_entry.insert(0, '1')


# Retrieve Previous Bill
def retrieve_bill():
    order_id_text = retrieve_entry.get().strip()

    if not order_id_text.isdigit():
        messagebox.showerror('Invalid Order ID', 'Enter a numeric Order ID.')
        return

    order_id = int(order_id_text)

    cur.execute('''
        SELECT order_id, order_date, subtotal, food_gst,
        packaged_gst, total, people
        FROM orders
        WHERE order_id = ?
    ''', (order_id,))

    bill = cur.fetchone()

    if bill is None:
        messagebox.showinfo('Not Found', 'No bill found for this Order ID.')
        return

    cur.execute('''
        SELECT item_id, item_name, quantity, price
        FROM order_items
        WHERE order_id = ?
    ''', (order_id,))

    saved_items = cur.fetchall()

    invoice = 'ORDER ID: ' + str(bill[0])
    invoice = invoice + '\nDate: ' + str(bill[1])
    invoice = invoice + '\n\nItem ID | Item Name | Qty | Amount'
    invoice = invoice + '\n--------------------------------\n'

    for item_id, name, quantity, price in saved_items:
        invoice = invoice + str(item_id) + ' | ' + name
        invoice = invoice + ' | ' + str(quantity)
        invoice = invoice + ' | Rs. ' + str(round(price * quantity, 2))
        invoice = invoice + '\n'

    invoice = invoice + '\nSubtotal: Rs. ' + str(round(bill[2], 2))
    invoice = invoice + '\nFood GST (5%): Rs. ' + str(round(bill[3], 2))
    invoice = invoice + '\nPackaged GST (18%): Rs. ' + str(round(bill[4], 2))
    invoice = invoice + '\nFINAL BILL: Rs. ' + str(round(bill[5], 2))
    invoice = invoice + '\nPeople: ' + str(bill[6])

    messagebox.showinfo('Previous Bill', invoice)


# GUI
root = tk.Tk()
root.title('Restaurant Billing System')
root.geometry('950x760')
root.minsize(850, 650)

tk.Label(
    root,
    text='RESTAURANT BILLING SYSTEM',
    font=('Arial', 18, 'bold')
).grid(row=0, column=0, columnspan=4, pady=12)


# Menu Frame
menu_frame = ttk.LabelFrame(root, text='Menu')
menu_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=8, sticky='nsew')

ttk.Label(menu_frame, text='Category:').grid(row=0, column=0, padx=5, pady=5)

category_box = ttk.Combobox(
    menu_frame,
    values=list(MENU.keys()),
    state='readonly',
    width=20
)

category_box.grid(row=0, column=1, padx=5, pady=5)
category_box.set('Starters')
category_box.bind('<<ComboboxSelected>>', show_menu)

menu_tree = ttk.Treeview(
    menu_frame,
    columns=('sr', 'id', 'name', 'price'),
    displaycolumns=('sr', 'name', 'price'),
    show='headings',
    height=10
)

menu_tree.heading('sr', text='Sr. No.')
menu_tree.heading('id', text='Item ID')
menu_tree.heading('name', text='Item Name')
menu_tree.heading('price', text='Price')

menu_tree.column('sr', width=65, anchor='center')
menu_tree.column('id', width=0, minwidth=0, stretch=False)
menu_tree.column('name', width=220)
menu_tree.column('price', width=100, anchor='e')

menu_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

ttk.Label(menu_frame, text='Quantity:').grid(row=2, column=0, padx=5, pady=5)

quantity_box = ttk.Spinbox(menu_frame, from_=1, to=100, width=7)
quantity_box.set(1)
quantity_box.grid(row=2, column=1, padx=5, pady=5, sticky='w')

ttk.Button(
    menu_frame,
    text='Add to Order',
    command=add_item
).grid(row=3, column=0, columnspan=2, padx=5, pady=6)


# Current Order Frame
order_frame = ttk.LabelFrame(root, text='Current Order')
order_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=8, sticky='nsew')

order_tree = ttk.Treeview(
    order_frame,
    columns=('sr', 'id', 'name', 'qty', 'price', 'amount'),
    displaycolumns=('sr', 'name', 'qty', 'price', 'amount'),
    show='headings',
    height=10
)

order_tree.heading('sr', text='Sr. No.')
order_tree.heading('id', text='Item ID')
order_tree.heading('name', text='Item Name')
order_tree.heading('qty', text='Qty')
order_tree.heading('price', text='Price')
order_tree.heading('amount', text='Amount')

order_tree.column('sr', width=55, anchor='center')
order_tree.column('id', width=0, minwidth=0, stretch=False)
order_tree.column('name', width=145)
order_tree.column('qty', width=45, anchor='center')
order_tree.column('price', width=80, anchor='e')
order_tree.column('amount', width=90, anchor='e')

order_tree.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

ttk.Button(
    order_frame,
    text='Remove Selected',
    command=remove_item
).grid(row=1, column=0, padx=5, pady=5)


# Bill Summary
summary_frame = ttk.LabelFrame(root, text='Bill Summary')
summary_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=8, sticky='ew')

subtotal_label = ttk.Label(summary_frame, text='Subtotal: Rs. 0.00')
subtotal_label.grid(row=0, column=0, padx=8, pady=4, sticky='w')

total_label = ttk.Label(
    summary_frame,
    text='Final Total: Rs. 0.00',
    font=('Arial', 14, 'bold')
)

total_label.grid(row=1, column=0, padx=8, pady=4, sticky='w')

gst_label = ttk.Label(
    summary_frame,
    text='Food GST (5%): Rs. 0.00 | Packaged GST (18%): Rs. 0.00',
    font=('Arial', 8),
    foreground='gray'
)

gst_label.grid(row=2, column=0, columnspan=3, padx=8, pady=3, sticky='w')

ttk.Label(summary_frame, text='Split between people:').grid(
    row=3, column=0, padx=8, pady=5, sticky='w'
)

people_entry = ttk.Entry(summary_frame, width=7)
people_entry.insert(0, '1')
people_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

ttk.Button(
    summary_frame,
    text='Generate Final Bill',
    command=save_bill
).grid(row=3, column=2, padx=8, pady=5)


# Bill History
history_frame = ttk.LabelFrame(root, text='Bill History')
history_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=8, sticky='ew')

ttk.Label(history_frame, text='Order ID:').grid(row=0, column=0, padx=5, pady=5)

retrieve_entry = ttk.Entry(history_frame, width=12)
retrieve_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(
    history_frame,
    text='Check Previous Bill',
    command=retrieve_bill
).grid(row=0, column=2, padx=5, pady=5)


# Layout
for column in range(4):
    root.columnconfigure(column, weight=1)

root.rowconfigure(1, weight=1)

menu_frame.columnconfigure(0, weight=1)
menu_frame.columnconfigure(1, weight=1)
menu_frame.rowconfigure(1, weight=1)

order_frame.columnconfigure(0, weight=1)
order_frame.columnconfigure(1, weight=1)
order_frame.rowconfigure(0, weight=1)


# Run Application
show_menu()
update_total()


def close_app():
    con.close()
    root.destroy()


root.protocol('WM_DELETE_WINDOW', close_app)
root.mainloop()
