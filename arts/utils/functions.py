# ============================================
# ARTS - Accounts Receivable Tracking System
# utils/functions.py - Shared Functions
# Converted from FUNCTION.PRG / BOXHEAD.PRG
# ============================================

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

# Party type codes
PARTY_TYPES = {
    "C" : "Customer",
    "B" : "Broker",
    "X" : "Both (Customer & Broker)"
}

# Bill To options
BILLTO_OPTIONS = {
    "CUST" : "Customer",
    "CONS" : "Consignee",
    "BROK" : "Broker",
    "SHPR" : "Shipper"
}

def find_party(code):
    """Find any party by code"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM party WHERE code = ?",
        (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def search_parties(term, party_type=None):
    """
    Search parties by name or lookupid.
    party_type: C=Customers only,
                B=Brokers only,
                None=All parties
    """
    conn = get_connection()
    cursor = conn.cursor()

    if party_type:
        cursor.execute("""
            SELECT * FROM party
            WHERE (name LIKE ?
            OR lookupid LIKE ?
            OR code LIKE ?)
            AND party_type IN (?, 'X')
            AND active = 'Y'
            ORDER BY name
        """, (f"%{term}%", f"%{term}%",
              f"%{term}%", party_type))
    else:
        cursor.execute("""
            SELECT * FROM party
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

def get_billing_party(billto, custmr,
                      cnsnee, broker, shipper):
    """
    Resolves billing party code based on
    BILL TO selection.
    Business Rule: Any party can pay the bill.
    """
    mapping = {
        "CUST" : custmr,
        "CONS" : cnsnee,
        "BROK" : broker,
        "SHPR" : shipper
    }
    billcod = mapping.get(billto, custmr)
    return find_party(billcod)