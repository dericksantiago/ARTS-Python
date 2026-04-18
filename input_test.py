# Lesson 3 - User Input with proper data types

customer_name = input("Enter Customer Name: ")
invoice_amount = float(input("Enter Invoice Amount: "))
quantity = int(input("Enter Quantity: "))

total = invoice_amount * quantity

print("-----------------------------")
print("Customer:", customer_name)
print("Amount:  $", invoice_amount)
print("Quantity:", quantity)
print("Total:   $", total)
print("-----------------------------")