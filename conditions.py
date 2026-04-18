# Lesson 4 - Conditions
# Adding validation to our invoice entry

customer_name = input("Enter Customer Name: ")
invoice_amount = float(input("Enter Invoice Amount: "))
quantity = float(input("Enter Quantity: "))

# Validate customer name
if customer_name == "":
    print("Error: Customer name cannot be empty!")

# Validate invoice amount
elif invoice_amount <= 0:
    print("Error: Invoice amount must be greater than zero!")

# Validate quantity
elif quantity <= 0:
    print("Error: Quantity must be greater than zero!")

# Everything is valid - calculate and display
else:
    total = invoice_amount * quantity
    tax = total * 0.10
    grand_total = total + tax

    print("-----------------------------")
    print("Customer:    ", customer_name)
    print("Amount:     $", invoice_amount)
    print("Quantity:    ", quantity)
    print("Subtotal:   $", total)
    print("Tax (10%):  $", tax)
    print("Grand Total:$", grand_total)
    print("-----------------------------")