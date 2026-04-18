# ============================================
# ARTS - Almar Reporting and Tracking System
# modules/customers.py - Customer Module
# Converted from TM10.PRG / TBLUPD.PRG
# ============================================

import sqlite3
from ..utils.database import get_connection
from ..utils.functions import (show_header, show_footer,
    format_currency, pad_right, press_any_key,
    get_valid_string, get_valid_float, confirm)
from ..utils.errors import CustomerNotFound, DuplicateRecord

# ---- CUSTOMER QUERIES ----

def get_all_customers():
    """Returns all customers ordered by name"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM customer ORDER BY custnam")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def find_customer(code):
    """Find customer by code"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM customer WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise CustomerNotFound(
            f"Customer '{code}' not found!")
    return dict(row)

def search_customers(search_term):
    """Search customers by name or code"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM customer
        WHERE custnam LIKE ? OR code LIKE ?
        ORDER BY custnam
    """, (f"%{search_term}%", f"%{search_term}%"))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---- CUSTOMER DISPLAY ----

def list_customers():
    """
    Displays customer list with details panel.
    Mirrors ARTS Customer Table screen.
    """
    customers = get_all_customers()

    if not customers:
        print("  ⚠️  No customers found!")
        return

    show_header("CUSTOMER TABLE")
    print(f"  {'CODE':<6} {'CUSTOMER NAME':<28}"
          f"{'PHONE':<14} {'RATE':>8}")
    print("  " + "-" * 58)

    for c in customers:
        print(f"  {pad_right(c['code'],6)}"
              f"{pad_right(c['custnam'],28)}"
              f"{pad_right(c['phone'],14)}"
              f"{format_currency(c['rate']):>8}")

    show_footer()
    print(f"  Total customers: {len(customers)}")

def show_customer(code):
    """Shows full customer details"""
    try:
        c = find_customer(code)
        show_header("CUSTOMER DETAILS")
        print(f"  CODE      : {c['code']}")
        print(f"  LOOKUP ID : {c['lookupid']}")
        print(f"  NAME      : {c['custnam']}")
        print(f"  ADDRESS   : {c['street']}")
        print(f"  CITY      : {c['city']}")
        print(f"  ZIP       : {c['zip']}")
        print(f"  PHONE     : {c['phone']}")
        print(f"  FAX       : {c['fax']}")
        print(f"  ATTENTION : {c['attn']}")
        print(f"  SHIP TO   : {c['shipto']}")
        print(f"  SHIP FROM : {c['shipfm']}")
        print(f"  RATE      : {format_currency(c['rate'])}")
        show_footer()
    except CustomerNotFound as e:
        print(f"  ⚠️  {e}")

# ---- CUSTOMER OPERATIONS ----

def add_customer():
    """
    Interactive customer entry screen.
    Mirrors ARTS Customer Table Add screen.
    """
    show_header("ADD NEW CUSTOMER")
    try:
        code     = get_valid_string(
            "Customer Code (4 chars)  : ",
            max_length=4)
        lookupid = get_valid_string(
            "Lookup ID    (7 chars)   : ",
            max_length=7)
        custnam  = get_valid_string(
            "Customer Name (25 chars) : ",
            max_length=25)
        street   = get_valid_string(
            "Street Address           : ",
            required=False)
        city     = get_valid_string(
            "City                     : ",
            required=False)
        zip_code = get_valid_string(
            "ZIP Code                 : ",
            max_length=5, required=False)
        phone    = get_valid_string(
            "Phone                    : ",
            max_length=12, required=False)
        fax      = get_valid_string(
            "Fax                      : ",
            max_length=12, required=False)
        attn     = get_valid_string(
            "Attention                : ",
            max_length=15, required=False)
        shipto   = get_valid_string(
            "Ship To                  : ",
            max_length=20, required=False)
        shipfm   = get_valid_string(
            "Ship From                : ",
            max_length=20, required=False)
        rate     = get_valid_float(
            "Rate                   $ : ",
            min_val=0)

        if not confirm(
            f"Add customer '{custnam}'?"):
            print("  ❌ Cancelled.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customer VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (code.upper(), lookupid.upper(),
              custnam, street, city, zip_code,
              phone, fax, attn, shipto, shipfm, rate))
        conn.commit()
        conn.close()
        print(f"  ✅ Customer '{custnam}' added!")

    except sqlite3.IntegrityError:
        print(f"  ⚠️  Customer code already exists!")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def edit_customer(code):
    """
    Edit existing customer rate.
    Mirrors C=Change in ARTS Customer screen.
    """
    try:
        c = find_customer(code)
        show_header("EDIT CUSTOMER")
        print(f"  Customer : {c['custnam']}")
        print(f"  Current Rate: {format_currency(c['rate'])}")

        new_rate = get_valid_float(
            "New Rate $ : ", min_val=0)

        if confirm(f"Update rate to "
                   f"{format_currency(new_rate)}?"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE customer
                SET rate = ?
                WHERE code = ?
            """, (new_rate, code))
            conn.commit()
            conn.close()
            print("  ✅ Customer rate updated!")

    except CustomerNotFound as e:
        print(f"  ⚠️  {e}")

def delete_customer(code):
    """
    Delete a customer record.
    Mirrors D=Delete in ARTS Customer screen.
    """
    try:
        c = find_customer(code)
        if confirm(
            f"Delete customer '{c['custnam']}'? "
            f"THIS CANNOT BE UNDONE!"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM customer WHERE code = ?",
                (code,))
            conn.commit()
            conn.close()
            print(f"  ✅ Customer deleted!")
        else:
            print("  ❌ Cancelled.")

    except CustomerNotFound as e:
        print(f"  ⚠️  {e}")

# ---- CUSTOMER MENU ----

def customer_menu():
    """
    Customer Table main menu.
    Mirrors ARTS Customer Table screen navigation.
    C=Change, A=Add, D=Delete, F=Find, \\=QUIT
    """
    while True:
        list_customers()
        print("\n  C=Change  A=Add  D=Delete"
              "  F=Find  \\=Quit")
        show_footer()
        choice = input("  CHOICE: ").strip().upper()

        if choice == "A":
            add_customer()
            press_any_key()

        elif choice == "C":
            code = get_valid_string(
                "Enter Customer Code to change: ")
            edit_customer(code.upper())
            press_any_key()

        elif choice == "D":
            code = get_valid_string(
                "Enter Customer Code to delete: ")
            delete_customer(code.upper())
            press_any_key()

        elif choice == "F":
            term = get_valid_string(
                "Search by name or code: ")
            results = search_customers(term)
            if results:
                show_header("SEARCH RESULTS")
                for c in results:
                    print(f"  {c['code']:<6}"
                          f"{c['custnam']:<28}"
                          f"{format_currency(c['rate']):>8}")
                show_footer()
            else:
                print("  ⚠️  No results found!")
            press_any_key()

        elif choice == "\\":
            break

        else:
            print("  ⚠️  Invalid choice!")