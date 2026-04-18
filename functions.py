# ============================================
# ARTS - Accounts Receivable Tracking System
# functions.py - Shared Functions Library
# Converted from Clipper FUNCTION.PRG
# ============================================

# ---- DISPLAY FUNCTIONS ----

def show_header(title):
    """Displays a formatted screen header - like BOXHEAD.PRG in Clipper"""
    print("=" * 50)
    print(f"  ARTS - {title}")
    print("=" * 50)

def show_menu(title, options):
    """Displays a numbered menu and returns the user's choice"""
    show_header(title)
    for number, option in options.items():
        print(f"  [{number}] {option}")
    print("=" * 50)
    choice = input("  CHOICE: ").strip()
    return choice

def press_any_key():
    """Pauses and waits for user - like PRESS.PRG in Clipper"""
    input("\n  Press ENTER to continue...")

# ---- VALIDATION FUNCTIONS ----

def is_valid_amount(amount):
    """Returns True if amount is a positive number"""
    try:
        return float(amount) > 0
    except ValueError:
        return False

def is_valid_date(date_str):
    """Returns True if date is in MM/DD/YYYY format"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
        return True
    except ValueError:
        return False

# ---- FORMATTING FUNCTIONS ----

def format_currency(amount):
    """Formats a number as currency - e.g. 620.0 becomes $620.00"""
    return f"${float(amount):,.2f}"

def format_date(date_str):
    """Formats a date string for display"""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%m/%d/%Y")
        return dt.strftime("%m/%d/%Y")
    except:
        return date_str

# ---- CALCULATION FUNCTIONS ----

def calc_balance_due(rate, congestion=0, port_fee=0, admin_fee=0,
                     drop_chg=0, overweight=0, genset=0,
                     reefer=0, yard=0, transfer_fee=0,
                     misc1=0, misc2=0, misc3=0):
    """
    Calculates total invoice balance due.
    Mirrors the invoice calculation in INV10.PRG
    """
    total = (rate + congestion + port_fee + admin_fee +
             drop_chg + overweight + genset + reefer +
             yard + transfer_fee + misc1 + misc2 + misc3)
    return round(total, 2)

def calc_amount_paid(payments):
    """
    Calculates total amount paid from a list of payments.
    payments = list of payment amounts
    """
    return round(sum(payments), 2)

def calc_balance(original, amount_paid):
    """Calculates remaining balance due"""
    return round(original - amount_paid, 2)

# ---- MAIN PROGRAM - Test all functions ----

if __name__ == "__main__":

    # Test show_header
    show_header("ACCOUNTS RECEIVABLE")

    # Test show_menu
    options = {
        "1": "Delivery Order",
        "2": "Invoice",
        "3": "Payments",
        "4": "Customer Table",
        "\\": "QUIT"
    }
    choice = show_menu("MAIN MENU", options)
    print(f"\nYou selected: {choice}")

    # Test formatting functions
    print("\n--- Testing Format Functions ---")
    print(format_currency(620))
    print(format_currency(1234.5))
    print(format_date("07/31/2016"))

    # Test validation functions
    print("\n--- Testing Validation Functions ---")
    print(f"Is 620 valid amount? {is_valid_amount(620)}")
    print(f"Is -10 valid amount? {is_valid_amount(-10)}")
    print(f"Is 07/31/2016 valid date? {is_valid_date('07/31/2016')}")
    print(f"Is 13/01/2016 valid date? {is_valid_date('13/01/2016')}")

    # Test calculation functions - using real ARTS invoice data!
    print("\n--- Testing Calculation Functions ---")
    balance = calc_balance_due(rate=620, congestion=0, port_fee=0)
    print(f"Balance Due: {format_currency(balance)}")

    paid = calc_amount_paid([300, 320])
    print(f"Amount Paid: {format_currency(paid)}")

    remaining = calc_balance(620, paid)
    print(f"Remaining: {format_currency(remaining)}")

    press_any_key()