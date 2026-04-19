# ============================================
# ARTS - Accounts Receivable Tracking System
# modules/parties.py - Party Module
# Replaces customers.py and brokers.py
# Schema v4.0 - Party/Role model
# ============================================

import sqlite3
from ..utils.database import get_connection
from ..utils.functions import (
    show_header, show_footer, format_currency,
    pad_right, press_any_key, get_valid_string,
    get_valid_float, get_valid_date, confirm,
    generate_next_code, generate_lookup_id,
    search_parties, find_party,
    PARTY_TYPES, CHARGE_TYPES)
from ..utils.errors import CustomerNotFound

# ---- PARTY DISPLAY ----

def list_parties(party_type=None):
    """
    Lists all parties.
    party_type: C=Customers, B=Brokers, None=All
    """
    conn = get_connection()
    cursor = conn.cursor()

    if party_type:
        cursor.execute("""
            SELECT * FROM party
            WHERE party_type IN (?, 'X')
            AND active = 'Y'
            ORDER BY name
        """, (party_type,))
    else:
        cursor.execute("""
            SELECT * FROM party
            WHERE active = 'Y'
            ORDER BY name
        """)

    rows = cursor.fetchall()
    conn.close()
    parties = [dict(r) for r in rows]

    title = {
        "C": "CUSTOMER TABLE",
        "B": "BROKER TABLE",
        None: "ALL PARTIES"
    }.get(party_type, "PARTY TABLE")

    show_header(title)

    if not parties:
        print("  ⚠️  No records found!")
        show_footer()
        return

    print(f"  {'CODE':<6} {'NAME':<28}"
          f"{'PHONE':<13} {'TYPE':>4}")
    print("  " + "-" * 55)

    for p in parties:
        ptype = PARTY_TYPES.get(
            p['party_type'], p['party_type'])[:4]
        print(f"  {pad_right(p['code'],6)}"
              f"{pad_right(p['name'],28)}"
              f"{pad_right(p['phone'],13)}"
              f"{ptype:>4}")

    show_footer()
    print(f"  Total: {len(parties)}")

def show_party(code):
    """Shows full party details"""
    p = find_party(code)
    if not p:
        print(f"  ⚠️  Party '{code}' not found!")
        return

    show_header("PARTY DETAILS")
    print(f"  CODE      : {p['code']}")
    print(f"  LOOKUP ID : {p['lookupid']}")
    print(f"  NAME      : {p['name']}")
    print(f"  TYPE      : "
          f"{PARTY_TYPES.get(p['party_type'])}")
    print(f"  ADDRESS   : {p['street']}")
    print(f"  CITY      : {p['city']}")
    print(f"  ZIP       : {p['zip']}")
    print(f"  PHONE     : {p['phone']}")
    print(f"  FAX       : {p['fax']}")
    print(f"  ATTENTION : {p['attn']}")
    show_footer()

# ---- PARTY OPERATIONS ----

def add_party(party_type="C"):
    """
    Interactive party entry screen.
    party_type: C=Customer, B=Broker, X=Both
    """
    titles = {
        "C": "ADD NEW CUSTOMER",
        "B": "ADD NEW BROKER",
        "X": "ADD NEW PARTY"
    }
    show_header(titles.get(party_type,
                           "ADD NEW PARTY"))
    print("  (Type \\ at any field to cancel)\n")

    try:
        name = get_valid_string(
            "Name         (25 chars)  : ",
            max_length=25)
        if name == "\\":
            print("  ❌ Cancelled.")
            return

        # Auto-generate code and lookupid
        code     = generate_next_code("party")
        lookupid = generate_lookup_id(name)
        print(f"  ℹ️  Code assigned : {code}")
        print(f"  ℹ️  Lookup ID     : {lookupid}")

        street = get_valid_string(
            "Street Address           : ",
            required=False)
        if street == "\\":
            print("  ❌ Cancelled.")
            return

        city = get_valid_string(
            "City                     : ",
            required=False)
        if city == "\\":
            print("  ❌ Cancelled.")
            return

        zip_code = get_valid_string(
            "ZIP Code                 : ",
            max_length=5, required=False)
        if zip_code == "\\":
            print("  ❌ Cancelled.")
            return

        phone = get_valid_string(
            "Phone                    : ",
            max_length=12, required=False)
        if phone == "\\":
            print("  ❌ Cancelled.")
            return

        fax = get_valid_string(
            "Fax                      : ",
            max_length=12, required=False)
        if fax == "\\":
            print("  ❌ Cancelled.")
            return

        attn = get_valid_string(
            "Attention                : ",
            max_length=15, required=False)
        if attn == "\\":
            print("  ❌ Cancelled.")
            return

        if not confirm(
            f"Add '{name}' as "
            f"{PARTY_TYPES.get(party_type)}?"):
            print("  ❌ Cancelled.")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO party VALUES
            (?,?,?,?,?,?,?,?,?,?,'Y')
        """, (code, lookupid, name,
              street, city, zip_code,
              phone, fax, attn, party_type))
        conn.commit()
        conn.close()
        print(f"  ✅ '{name}' added "
              f"with code {code}!")

    except sqlite3.IntegrityError:
        print(f"  ⚠️  Code already exists!")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def manage_party_rates(code):
    """Manages rate schedule for a party"""
    p = find_party(code)
    if not p:
        print(f"  ⚠️  Party '{code}' not found!")
        return

    show_header(f"RATE SCHEDULE — {p['name']}")

    # Show current rates
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT charge_type, amount,
               effective_date
        FROM party_rates
        WHERE party_code = ?
        AND active = 'Y'
        ORDER BY charge_type
    """, (code,))
    rates = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if rates:
        print(f"  {'CHARGE TYPE':<20}"
              f"{'RATE':>10}  {'EFF DATE'}")
        print("  " + "-" * 45)
        for r in rates:
            print(f"  {r['charge_type']:<20}"
                  f"${r['amount']:>9.2f}  "
                  f"{r['effective_date']}")
    else:
        print("  ⚠️  No rates set up yet!")

    show_footer()
    print("\n  [A] Add/Update rate  [\\] Back")
    choice = input("\n  CHOICE: ").strip().upper()

    if choice == "A":
        show_header("SELECT CHARGE TYPE")
        for i, ct in enumerate(CHARGE_TYPES, 1):
            print(f"  [{i:2}] {ct}")
        show_footer()

        sel = input(
            "  Select charge type #: ").strip()
        try:
            charge_type = CHARGE_TYPES[int(sel)-1]
            amount = get_valid_float(
                f"Rate for {charge_type}: $",
                min_val=0)
            eff_date = get_valid_date(
                "Effective Date (MM/DD/YYYY): ")

            # Deactivate old rate
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE party_rates
                SET active = 'N',
                    end_date = ?
                WHERE party_code = ?
                AND charge_type = ?
                AND active = 'Y'
            """, (eff_date, code, charge_type))

            # Insert new rate
            cursor.execute("""
                INSERT INTO party_rates
                (party_code, charge_type,
                 amount, effective_date, active)
                VALUES (?,?,?,?,'Y')
            """, (code, charge_type,
                  amount, eff_date))
            conn.commit()
            conn.close()
            print(f"  ✅ {charge_type} rate set "
                  f"to ${amount:.2f}!")

        except (ValueError, IndexError):
            print("  ⚠️  Invalid selection!")

# ---- PARTY MENUS ----

def party_menu(party_type=None):
    """
    Party management menu.
    party_type: C=Customers, B=Brokers, None=All
    """
    while True:
        list_parties(party_type)
        print("\n  C=Change  A=Add  D=Delete"
              "  F=Find  R=Rates  \\=Quit")
        show_footer()
        choice = input("  CHOICE: ").strip().upper()

        if choice == "A":
            add_party(party_type or "C")
            press_any_key()

        elif choice == "C":
            code = get_valid_string(
                "Enter Code to change: ")
            p = find_party(code.upper())
            if p:
                show_party(code.upper())
                press_any_key()
            else:
                print(f"  ⚠️  Not found!")

        elif choice == "D":
            code = get_valid_string(
                "Enter Code to delete: ")
            p = find_party(code.upper())
            if p:
                if confirm(
                    f"Delete '{p['name']}'? "
                    f"CANNOT BE UNDONE!"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE party
                        SET active = 'N'
                        WHERE code = ?
                    """, (code.upper(),))
                    conn.commit()
                    conn.close()
                    print("  ✅ Record deactivated!")
            else:
                print("  ⚠️  Not found!")
            press_any_key()

        elif choice == "F":
            term = get_valid_string(
                "Search by name or code: ")
            results = search_parties(
                term, party_type)
            if results:
                show_header("SEARCH RESULTS")
                for p in results:
                    print(f"  {p['code']:<6}"
                          f"{p['name']:<28}"
                          f"{p['phone']:<13}")
                show_footer()
            else:
                print("  ⚠️  No results found!")
            press_any_key()

        elif choice == "R":
            code = get_valid_string(
                "Enter Code for rates: ")
            manage_party_rates(code.upper())
            press_any_key()

        elif choice == "\\":
            break

        else:
            print("  ⚠️  Invalid choice!")

# Convenience functions for menu
def customer_menu():
    """Shows customer view of party table"""
    party_menu(party_type="C")

def broker_menu():
    """Shows broker view of party table"""
    party_menu(party_type="B")