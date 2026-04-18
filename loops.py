# Lesson 5 - Loops
# Entering multiple invoice line items

customer_name = input("Enter Customer Name: ")

# Empty list to store line items (we'll learn lists properly soon!)
line_items = []
total = 0

# Keep asking for items until user says done
while True:
    print("\n-----------------------------")
    item_name = input("Enter Item Description (or 'done' to finish): ")

    # Exit loop when user types 'done'
    if item_name.lower() == "done":
        break

    price = float(input("Enter Unit Price: $"))
    quantity = float(input("Enter Quantity: "))

    # Validate inputs
    if price <= 0 or quantity <= 0:
        print("⚠️  Price and quantity must be greater than zero. Try again.")
        continue

    subtotal = price * quantity
    total += subtotal

    # Store the item
    line_items.append(f"{item_name} | ${price:.2f} x {quantity} = ${subtotal:.2f}")

# Display the invoice
print("\n================================")
print("         INVOICE SUMMARY")
print("================================")
print(f"Customer: {customer_name}")
print("--------------------------------")

for item in line_items:
    print(item)

print("--------------------------------")
tax = total * 0.10
grand_total = total + tax
print(f"Subtotal:    ${round(total, 2):.2f}")
print(f"Tax (10%):   ${round(tax, 2):.2f}")
print(f"Grand Total: ${round(grand_total, 2):.2f}")
print("================================")
