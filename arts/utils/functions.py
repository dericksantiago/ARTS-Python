# ============================================
# ARTS - Accounts Receivable Tracking System
# utils/functions.py - Shared Functions
# Converted from FUNCTION.PRG / BOXHEAD.PRG
# ============================================

from .database import get_connection
from datetime import datetime
from .errors import InvalidDate, InvalidAmount


# ---- DISPLAY FUNCTIONS ----

def draw_box(lines, width=55):
    """
    Wraps a list of strings in a colored box.
    """
    from colorama import init, Fore, Style
    init()

    COLOR = Fore.GREEN
    RESET = Style.RESET_ALL

    # Top border
    print(f"{COLOR}╔" + "═" * (width - 2) + "╗")

    # Content lines
    for line in lines:
        print("║" + line.center(width - 2) + "║")

    # Bottom border
    print("╚" + "═" * (width - 2) + f"╝{RESET}")

def show_header(title):
    """Displays formatted screen header"""
    print("\n" + "=" * 55)
    print(f"  ARTS  —  {title}")
    print("=" * 55)

def show_footer():
    """Displays screen footer"""
    print("=" * 55)

def show_menu(title, options):
    """Displays a numbered menu and returns user choice"""
    show_header(title)
    for key, label in options.items():
        print(f"    [{key}]  {label}")
    show_footer()
    return input("  CHOICE: ").strip().upper()

def press_any_key():
    """Pauses for user - like PRESS.PRG in Clipper"""
    input("\n  Press ENTER to continue...")

def confirm(message):
    """
    Asks yes/no question - like ASK.PRG in Clipper
    Returns True if user says Y
    """
    answer = input(f"\n  {message} (Y/N): ").strip().upper()
    return answer == "Y"

# ---- FORMATTING FUNCTIONS ----

def format_currency(amount):
    """Formats number as currency - $1,234.56"""
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"

def format_date(date_str):
    """Formats date string for display MM/DD/YYYY"""
    try:
        dt = datetime.strptime(str(date_str), "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except:
        return date_str or ""

def pad_right(text, width):
    """Left aligns text in fixed width - like PADR() in Clipper"""
    return str(text or "")[:width].ljust(width)

def pad_left(text, width):
    """Right aligns text in fixed width - like PADL() in Clipper"""
    return str(text or "")[:width].rjust(width)

# ---- VALIDATION FUNCTIONS ----

def validate_po_number(ponum):
    """Validates PO number - must be 9 digits"""
    from .errors import InvalidPONumber
    ponum = str(ponum).strip()
    if not ponum.isdigit() or len(ponum) != 9:
        raise InvalidPONumber(
            f"PO number must be 9 digits: '{ponum}'")
    return ponum

def validate_date(date_str):
    """Validates date in MM/DD/YYYY format"""
    try:
        datetime.strptime(date_str.strip(), "%m/%d/%Y")
        return date_str.strip()
    except ValueError:
        raise InvalidDate(
            f"Invalid date format: '{date_str}'. Use MM/DD/YYYY")

def validate_amount(amount):
    """Validates financial amount"""
    try:
        amount = float(amount)
        if amount < 0:
            raise InvalidAmount(
                f"Amount cannot be negative: {amount}")
        if amount > 999999.99:
            raise InvalidAmount(
                f"Amount exceeds maximum: {amount}")
        return amount
    except (TypeError, ValueError):
        raise InvalidAmount(f"Invalid amount: {amount}")

# ---- INPUT FUNCTIONS ----

def get_valid_float(prompt, min_val=None, max_val=None):
    """Keeps asking until valid number is entered"""
    while True:
        try:
            value = float(input(f"  {prompt}"))
            if min_val is not None and value < min_val:
                print(f"  ⚠️  Minimum value is {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠️  Maximum value is {max_val}")
                continue
            return value
        except ValueError:
            print("  ⚠️  Please enter a valid number!")

def get_valid_date(prompt):
    """Keeps asking until valid date is entered"""
    while True:
        try:
            date_str = input(f"  {prompt}").strip()
            return validate_date(date_str)
        except InvalidDate as e:
            print(f"  ⚠️  {e}")

def get_valid_string(prompt, max_length=None, required=True):
    """Keeps asking until valid string is entered"""
    while True:
        value = input(f"  {prompt}").strip()
        if required and not value:
            print("  ⚠️  This field is required!")
            continue
        if max_length and len(value) > max_length:
            print(f"  ⚠️  Maximum {max_length} characters!")
            continue
        return value

# ---- CALCULATION FUNCTIONS ----

def calc_balance_due(rate=0, congestion=0, port_fee=0,
                     admin_fee=0, drop_chg=0, overweight=0,
                     genset=0, reefer=0, yard=0,
                     transfer_fee=0, misc1=0,
                     misc2=0, misc3=0):
    """Calculates total invoice balance due"""
    total = (rate + congestion + port_fee + admin_fee +
             drop_chg + overweight + genset + reefer +
             yard + transfer_fee + misc1 + misc2 + misc3)
    return round(total, 2)

def calc_balance(original, amount_paid):
    """Calculates remaining balance"""
    return round(float(original) - float(amount_paid), 2)

def search_contacts(term, contact_type=None):
    """
    Search contacts by name or lookupid.
    contact_type: C=Customers only,
                B=Brokers only,
                None=All contacts
    """
    conn = get_connection()
    cursor = conn.cursor()

    if contact_type:
        cursor.execute("""
            SELECT * FROM contact
            WHERE (name LIKE ?
            OR lookupid LIKE ?
            OR code LIKE ?)
            AND contact_type IN (?, 'X')
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

def find_contact(code):
    """Find contact by code"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM contact WHERE code = ?",
        (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_billing_contact(billto, custmr,
                      cnsnee, broker, shipper):
    """
    Resolves billing contact code based on
    BILL TO selection.
    Business Rule: Any contact can pay the bill.
    """
    mapping = {
        "CUST" : custmr,
        "CONS" : cnsnee,
        "BROK" : broker,
        "SHPR" : shipper
    }
    billcod = mapping.get(billto, custmr)
    return find_contact(billcod)

# ---- CODE GENERATION FUNCTIONS ----

def generate_lookup_id(name):
    """
    Generates lookup ID from name.
    Takes first 7 chars, removes spaces,
    uppercase.
    e.g. "Karl Schroff & Associates" → "KARLSCH"
    """
    clean = ''.join(
        c for c in name
        if c.isalnum()).upper()
    return clean[:7]

def generate_next_code(table_name):
    """
    Generates next available 4-digit code.
    Finds highest existing code and adds 1.
    e.g. if highest is 0489 → returns 0490
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT MAX(CAST(code AS INTEGER))
            FROM {table_name}
        """)
        row = cursor.fetchone()
        max_code = row[0] if row[0] else 0
        next_code = max_code + 1
        return str(next_code).zfill(4)
    except:
        return "0001"
    finally:
        conn.close()

def generate_next_donum():
    """
    Generates next Delivery Order number.
    9 digits, zero padded.
    e.g. 000056648
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT MAX(CAST(donum AS INTEGER))
            FROM delivery_order
        """)
        row = cursor.fetchone()
        max_num = row[0] if row[0] else 0
        next_num = max_num + 1
        return str(next_num).zfill(9)
    except:
        return "000000001"
    finally:
        conn.close()


# Contact types
CONTACT_TYPES = {
    "CUSTOMER" : "Customer",
    "BROKER"   : "Broker",
    "TERMINAL" : "Terminal/Shipper",
    "BOTH"     : "Customer & Broker"
}

# Employee types
EMPLOYEE_TYPES = {
    "D" : "Driver",
    "S" : "Sub-hauler"
}

# Bill To options
BILLTO_OPTIONS = {
    "CUSTOMER"  : "Customer",
    "CONSIGNEE" : "Consignee",
    "BROKER"    : "Broker",
    "SHIPPER"   : "Shipper/Terminal"
}

# Charge types
CHARGE_TYPES = [
    "RATE",
    "CONGESTION",
    "PORT FEE",
    "ADMIN FEE",
    "DROP CHG",
    "OVERWEIGHT",
    "GENSET",
    "REEFER",
    "YARD",
    "TRANSFER FEE",
    "MISC 1",
    "MISC 2",
    "MISC 3",
]