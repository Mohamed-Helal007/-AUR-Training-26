def load_stock(filename="stock.txt"):
    stock = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                item, qty = line.strip().split(",")
                stock[item.lower()] = int(qty)
    except FileNotFoundError:
        print("Error: stock.txt not found")
    except Exception as e:
        print(f"Error reading file: {e}")
    return stock


def show_menu():
    print("\nEnter 1 to add stock")
    print("Enter 2 to remove stock")
    print("Enter 3 to show stock's contents")
    print("Enter 4 to exit")


def show_stock(stock):
    for idx, (item, qty) in enumerate(stock.items(), start=1):
        print(f"{idx}. {item}: {qty}")


def add_stock(stock):
    show_stock(stock)
    choice = input("Enter stock name or id: ").lower()
    if choice.isdigit():
        choice = list(stock.keys())[int(choice) - 1]  
    qty = int(input("Enter how much to add: "))
    if choice in stock:
        stock[choice] += qty
    else:
        stock[choice] = qty


def remove_stock(stock):
    show_stock(stock)
    choice = input("Enter stock name or id: ").lower()
    if choice.isdigit():
        choice = list(stock.keys())[int(choice) - 1]  
    if choice in stock:
        qty = int(input("Enter how much to remove: "))
        if stock[choice] - qty < 0:
            print("Error: cannot go below zero")
        else:
            stock[choice] -= qty
    else:
        print("Error: item not found.")


def save_exit(stock, filename="stock.txt"):
    with open(filename, "w") as f:
        for item, qty in stock.items():
            f.write(f"{item},{qty}\n")


def main():
    stock = load_stock()
    while True:
        show_menu()
        choice = input("Enter choice: ")  
        if choice == "1":
            add_stock(stock)
        elif choice == "2":
            remove_stock(stock)
        elif choice == "3":
            show_stock(stock)
        elif choice == "4":
            save_exit(stock)
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
