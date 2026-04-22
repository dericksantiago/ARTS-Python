# ============================================
# ARTS - Accounts Receivable Tracking System
# modules/contacts.py - contact Module
# Replaces customers.py and brokers.py
# Schema v4.0 - contact/Role model
# ============================================

import sqlite3
from ..utils.database import get_connection
from ..utils.functions import (
    show_header, show_footer, format_currency,
    pad_right, press_any_key, get_valid_string,
    get_valid_float, get_valid_date, confirm,
    generate_next_code, generate_lookup_id,
    CONTACT_TYPES, CHARGE_TYPES)
from ..utils.errors import CustomerNotFound

# ---- contact DISPLAY ----

def list_contacts(contact_type=None):
    """
    Lists all contacts.
    contact_type: CUSTOMER, BROKER,
                  TERMINAL, None=All
    """
    from ..utils.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    if contact_type:
        cursor.execute("""
            SELECT * FROM contact
            WHERE contact_type IN (?, 'BOTH')
            AND active = 'Y'
            ORDER BY name
        """, (contact_type,))
    else:
        cursor.execute("""
            SELECT * FROM contact
            WHERE active = 'Y'
            ORDER BY name
        """)

    rows = cursor.fetchall()
    conn.close()
    contacts = [dict(r) for r in rows]

    title = {
        "CUSTOMER" : "CUSTOMER TABLE",
        "BROKER"   : "BROKER TABLE",
        "TERMINAL" : "TERMINAL TABLE",
        None       : "ALL CONTACTS"
    }.get(contact_type, "CONTACT TABLE")

    show_header(title)

    if not contacts:
        print("  ⚠️  No records found!")
        show_footer()
        return

    print(f"  {'CODE':<6} {'NAME':<28}"
          f"{'PHONE':<13} {'TYPE'}")
    print("  " + "-" * 58)

    for p in contacts:
        ptype = CONTACT_TYPES.get(
            p['contact_type'],
            p['contact_type'])
        print(f"  {pad_right(p['code'],6)}"
              f"{pad_right(p['name'],28)}"
              f"{pad_right(p['phone'],13)}"
              f"{ptype}")

    show_footer()
    print(f"  Total: {len(contacts)}")

# ---- contact OPERATIONS ----

def add_contact(contact_type="CUSTOMER"):
    """
    Interactive contact entry screen.
    contact_type: CUSTOMER, BROKER,
                  TERMINAL, BOTH
    """
    titles = {
        "CUSTOMER" : "ADD NEW CUSTOMER",
        "BROKER"   : "ADD NEW BROKER",
        "TERMINAL" : "ADD NEW TERMINAL",
        "BOTH"     : "ADD NEW CONTACT"
    }
    show_header(titles.get(
        contact_type, "ADD NEW CONTACT"))
    print("  (Type \\ at any field to cancel)\n")

    try:
        name = get_valid_string(
            "Name         (25 chars)  : ",
            max_length=25)
        if name == "\\":
            print("  ❌ Cancelled.")
            return

        # Auto-generate code and lookupid
        code     = generate_next_code("contact")
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
            f"{CONTACT_TYPES.get(contact_type, 'Customer')}?"):
            print("  ❌ Cancelled.")
            return

        # Save to database
        conn = None
        try:
            from ..utils.database import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contact
                VALUES (?,?,?,?,?,?,?,?,?,?,'Y')
            """, (code, lookupid, name,
                  street, city, zip_code,
                  phone, fax, attn,
                  contact_type))
            conn.commit()
            print(f"  ✅ '{name}' added "
                  f"with code {code}!")

        except sqlite3.IntegrityError:
            print(f"  ⚠️  Code already exists!")
        except Exception as e:
            print(f"  ❌ Database error: {e}")
        finally:
            if conn:
                conn.close()

    except Exception as e:
        print(f"  ❌ Error: {e}")
def manage_contact_rates(code):
    """Manages rate schedule for a contact"""
    p = find_contact(code)
    if not p:
        print(f"  ⚠️  contact '{code}' not found!")
        return

    show_header(f"RATE SCHEDULE — {p['name']}")

    # Show current rates
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT charge_type, amount,
               effective_date
        FROM contact_rates
        WHERE contact_code = ?
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
                UPDATE contact_rates
                SET active = 'N',
                    end_date = ?
                WHERE contact_code = ?
                AND charge_type = ?
                AND active = 'Y'
            """, (eff_date, code, charge_type))

            # Insert new rate
            cursor.execute("""
                INSERT INTO contact_rates
                (contact_code, charge_type,
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

def find_contact(code):
    """Find contact by code"""
    from ..utils.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM contact WHERE code = ?",
        (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def search_contacts(term, contact_type=None):
    """Search contacts by name, code or lookupid"""
    from ..utils.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    if contact_type:
        cursor.execute("""
            SELECT * FROM contact
            WHERE (name LIKE ?
            OR lookupid LIKE ?
            OR code LIKE ?)
            AND contact_type IN (?, 'BOTH')
            AND active = 'Y'
            ORDER BY name
        """, (f"%{term}%", f"%{term}%",
              f"%{term}%", contact_type))
    else:
        cursor.execute("""
            SELECT * FROM contact
            WHERE (name LIKE ?
            OR lookupid LIKE ?
            OR code LIKE ?)
            AND active = 'Y'
            ORDER BY name
        """, (f"%{term}%", f"%{term}%",
              f"%{term}%"))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]        

# ---- contact MENUS ----

def contact_menu(contact_type=None):
    """
    contact management menu.
    contact_type: C=Customers, B=Brokers, None=All
    """
    while True:
        list_contacts(contact_type)
        print("\n  C=Change  A=Add  D=Delete"
              "  F=Find  R=Rates  \\=Quit")
        show_footer()
        choice = input("  CHOICE: ").strip().upper()

        if choice == "A":
            add_contact(contact_type)
            press_any_key()

        elif choice == "C":
            code = get_valid_string(
            "Enter Code to change: ")
            edit_contact(code.upper())
            press_any_key()
        
        elif choice == "D":
            code = get_valid_string(
                "Enter Code to delete: ")
            p = find_contact(code.upper())
            if p:
                if confirm(
                    f"Delete '{p['name']}'? "
                    f"CANNOT BE UNDONE!"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE contact
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
            results = search_contacts(
                term, contact_type)
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
            manage_contact_rates(code.upper())
            press_any_key()

        elif choice == "\\":
            break

        else:
            print("  ⚠️  Invalid choice!")


def edit_contact(code):
    """Edit existing contact details"""
    p = find_contact(code)
    if not p:
        print(f"  ⚠️  Contact '{code}' not found!")
        return

    show_header("EDIT CONTACT")
    print(f"  Code   : {p['code']}")
    print(f"  Name   : {p['name']}")
    print(f"  Phone  : {p['phone']}")
    print(f"  Fax    : {p['fax']}")
    print(f"  Attn   : {p['attn']}")
    print(f"  Type   : "
      f"{CONTACT_TYPES.get(p['contact_type'], p['contact_type'])}")
    print()
    print("  (Press Enter to keep current value)\n")

    try:
        name = get_valid_string(
            f"Name [{p['name']}]: ",
            max_length=25, required=False)
        street = get_valid_string(
            f"Street [{p['street']}]: ",
            required=False)
        city = get_valid_string(
            f"City [{p['city']}]: ",
            required=False)
        zip_code = get_valid_string(
            f"ZIP [{p['zip']}]: ",
            max_length=5, required=False)
        phone = get_valid_string(
            f"Phone [{p['phone']}]: ",
            max_length=12, required=False)
        fax = get_valid_string(
            f"Fax [{p['fax']}]: ",
            max_length=12, required=False)
        attn = get_valid_string(
            f"Attention [{p['attn']}]: ",
            max_length=15, required=False)

        if not confirm(
            f"Update contact '{p['name']}'?"):
            print("  ❌ Cancelled.")
            return

        from ..utils.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contact SET
            name    = CASE WHEN ? = ''
                     THEN name ELSE ? END,
            street  = CASE WHEN ? = ''
                     THEN street ELSE ? END,
            city    = CASE WHEN ? = ''
                     THEN city ELSE ? END,
            zip     = CASE WHEN ? = ''
                     THEN zip ELSE ? END,
            phone   = CASE WHEN ? = ''
                     THEN phone ELSE ? END,
            fax     = CASE WHEN ? = ''
                     THEN fax ELSE ? END,
            attn    = CASE WHEN ? = ''
                     THEN attn ELSE ? END
            WHERE code = ?
        """, (name, name, street, street,
              city, city, zip_code, zip_code,
              phone, phone, fax, fax,
              attn, attn, code))
        conn.commit()
        conn.close()
        print("  ✅ Contact updated!")

    except Exception as e:
        print(f"  ❌ Error: {e}")

# Convenience functions for menu
def customer_menu():
    """Shows customer view of contact table"""
    contact_menu(contact_type="C")

def broker_menu():
    """Shows broker view of contact table"""
    contact_menu(contact_type="B")