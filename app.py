#!/usr/bin/env python3
from collections import OrderedDict
import csv
import datetime
import sys
import os
import time



from peewee import *

db = SqliteDatabase("inventory.db")


class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

def initial_fill():
    with open("inventory.csv", newline="") as csvfile:
        inv_reader = csv.DictReader(csvfile, delimiter=",")
        rows = list(inv_reader)
        for item in rows:
            item["product_quantity"] = int(item["product_quantity"])
            item["product_price"] = round(float((item["product_price"].strip("$")))*100)
            item["date_updated"] = datetime.datetime.strptime(item["date_updated"], "%m/%d/%Y")
            try:
                Product.create(product_name=item["product_name"],
                    product_quantity=item["product_quantity"],
                    product_price=item["product_price"],
                    date_updated=item["date_updated"])

            except IntegrityError:

                product_record = Product.get(product_name = item["product_name"])

                if product_record.date_updated <= item["date_updated"]:
                    product_record.product_name = item["product_name"]
                    product_record.product_quantity = item["product_quantity"]
                    product_record.product_price = item["product_price"]
                    product_record.date_updated = item["date_updated"]
                    product_record.save()
                else:
                    pass

def add_new_products():
    """Add a new item to the database."""
    while True:
        try:
            new_pn = input("What is the name of the product that you would like to add?     ")
            new_pq = int(input("How many units are you adding?         "))
            new_uc = round(float(input("What is the unit cost? $"))*100)

        except ValueError:
            print("Hmmmm, something's not right, let's try that again!")
            continue
        try:
            adding_product = Product.create(
                product_name=new_pn,
                product_quantity=new_pq,
                product_price=new_uc,
                date_updated=datetime.datetime.now())
            print(f"\n{new_pn.title()} successfully added to the inventory!\n")
            time.sleep(2)
            clear()

        except IntegrityError:
            save_check = input("This product already exists in the inventory.\n[y] updates the existing item, [n] maintains current inventory.     ").lower().strip()
            if save_check != "n":
                product_record = Product.get(product_name = new_pn)
                product_record.product_quantity = new_pq
                product_record.product_price = new_uc
                #if date updated is less than date now change date
                product_record.date_updated = datetime.datetime.now()
                product_record.save()
                print(f"\n{new_pn.title()} saved successfully!\n")
                time.sleep(2)
                clear()
            else:
                print("Ok, this entry will cease to be.")
                time.sleep(2)
                clear()


        break



def initialize():
    """Create the database and the table if they don't exist"""
    db.connect()
    db.create_tables([Product], safe=True)


def display_id():
    """View item using product_id."""
    #getting and displaying a product by its product_id.
    while True:
        try:
            print("[R] returns to main menu.")
            user_query = input("Please select a product to view by ID number:  ").lower().strip()
            if user_query == "r":
                time.sleep(1)
                clear()
                menu_loop()
            else:
                user_query = int(user_query)

            product_id_query = Product.select(Product.product_id)
            product_ids = []
            for item in product_id_query:
                product_ids.append(item)

            if  user_query <= len(product_ids) and  user_query > 0:
                user_display = Product.select().where(Product.product_id==user_query)
                for item in user_display:
                    print("Product ID Number: " + str(item.product_id))
                    print("Product Name: " + str(item.product_name))
                    unit_price = float(item.product_price/100)
                    print("Product Unit Price: $" + "{:.2f}".format(unit_price))
                    print("Total Units In House: " + str(item.product_quantity))
                    print("Last inventory update: " + datetime.datetime.strftime(item.date_updated, "%H%MPST on %A, %b %d, %Y") + "\n\n")

            else:
                print("This item is not yet in our inventory. Try again.")
            continue
        except ValueError:
                print("Try again with a whole number.")
        continue
        break

def backup_db():
    """Back up database."""
    #Backs database up into csv file
    bu = "bu_inventory.csv"
    with open("bu_inventory.csv", "w") as bu_csvfile:
        fieldnames = ["product_name", "product_quantity", "product_price", "date_updated"]
        bu_writer = csv.DictWriter(bu_csvfile, fieldnames=fieldnames)

        bu_writer.writeheader()
        items = Product.select()
        for item in items:
            bu_writer.writerow({
                "product_name": item.product_name,
                "product_quantity": item.product_quantity,
                "product_price": item.product_price,
                "date_updated": item.date_updated
                })

    clear()
    print("All backed up as of {}.".format(datetime.datetime.now().strftime("%H%MPST on %A, %b %d, %Y")) + "\n")
    time.sleep(3)
    clear()


menu = OrderedDict([
    ("v", display_id),
    ("a", add_new_products),
    ("b", backup_db),
    ])

def menu_loop():
    """Return to main menu."""
    choice = None
    while choice != "q":
        try:
            print("\nEnter 'q' to quit.")
            for key, value in menu.items():
                print("{}) {}".format(key, value.__doc__))
            choice = input("\nAction:  ").lower().strip()

            if choice in menu:
                menu[choice]()
            else:
                print("\nPlease try again with one of the alphabetical choices to the left of the menu.\n")
            continue
        except ValueError:
            print("Please enter a valid integer.")
            continue

        keep_going = input("[R] returns to main menu, [C] Continue to add products.").lower().strip()
        if keep_going == "c":
            continue
        else:
            menu_loop()


def clear():
    os.system("cls" if os.name == "nt" else "clear")

wel_mess = "Welcome to the store inventory app."
wel_indent = round((70 - len(wel_mess))/2)

if __name__ == "__main__":
    print("="*70)
    print((" " * wel_indent) + wel_mess + "\n\n\n")
    initialize()
    initial_fill()
    menu_loop()
