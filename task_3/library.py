from abc import ABC, abstractmethod
from enum import Enum

class ItemStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    LOST = "Lost"

class LibraryItem(ABC):
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        LibraryItem.registry[cls.__name__] = cls  

    def __init__(self, title, status=ItemStatus.AVAILABLE):
        self.__status = status
        self.title = title

    @classmethod
    def from_dict(cls, data: dict):
        item_type = data.get("type")
        title = data.get("title")
        status_str = data.get("status", "AVAILABLE")

        try:
            status = ItemStatus[status_str]
        except KeyError:
            raise ValueError(f"Invalid status: {status_str}")

        subclass = cls.registry.get(item_type)
        if not subclass:
            raise ValueError(f"Unknown item type: {item_type}")
        clean_data = {k: v for k, v in data.items() if k not in ("type", "title", "status")}

        return subclass(title, status, **clean_data)

    def __lt__(self, other):
        return self.title < other.title

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title!r}, status={self.status})"

    def __str__(self):
        return f"{self.title} ({self.__class__.__name__}) - {self.status.value}"

    @property
    def status(self):
        return self.__status

    def checkout(self):
        if self.__status == ItemStatus.AVAILABLE:
            self.__status = ItemStatus.CHECKED_OUT
        else:
            raise ValueError("Item cannot be checked out unless it is available.")

    def return_item(self):
        if self.__status == ItemStatus.CHECKED_OUT:
            self.__status = ItemStatus.AVAILABLE
        else:
            raise ValueError("Item cannot be returned unless it is checked out.")

    def mark_lost(self):
        if self.__status != ItemStatus.LOST:
            self.__status = ItemStatus.LOST
        else:
            raise ValueError("Item is already marked as lost.")

    @abstractmethod
    def loan_period(self):
        pass

class Book(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, author=None, isbn=None, **kwargs):
        super().__init__(title, status)
        self.author = author
        self.isbn = isbn

    def loan_period(self):
        return 21

    @staticmethod
    def validate_isbn13(isbn: str) -> bool:
        isbn = isbn.replace("-", "")
        if len(isbn) != 13 or not isbn.isdigit():
            return False
        total = sum((int(digit) * (1 if i % 2 == 0 else 3)) for i, digit in enumerate(isbn[:-1]))
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(isbn[-1])

class DVD(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, director=None, **kwargs):
        super().__init__(title, status)
        self.director = director
    def loan_period(self):
        return 5

class Magazine(LibraryItem):
    def __init__(self, title, status=ItemStatus.AVAILABLE, issue=None, **kwargs):
        super().__init__(title, status)
        self.issue = issue
    def loan_period(self):
        return 14

class Database:
    def __init__(self, filename="database.txt"):
        self.filename = filename

    def load_data(self):
        items = []
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    parts = line.strip().split("|")
                    data = {}
                    for part in parts:
                        key, value = part.split("=", 1)
                        data[key] = value
                    item = LibraryItem.from_dict(data)
                    items.append(item)
        except FileNotFoundError:
            return []
        return items

    def save_items(self, items):
        with open(self.filename, "w") as f:
            for item in items:
                fields = [f"type={item.__class__.__name__}", f"title={item.title}", f"status={item.status.name}"]
                if isinstance(item, Book):
                    if item.author: fields.append(f"author={item.author}")
                    if item.isbn: fields.append(f"isbn={item.isbn}")
                elif isinstance(item, DVD):
                    if item.director: fields.append(f"director={item.director}")
                elif isinstance(item, Magazine):
                    if item.issue: fields.append(f"issue={item.issue}")
                f.write("|".join(fields) + "\n")

class Library:
    def __init__(self):
        self.items = []

    def add_item(self, item: LibraryItem):
        self.items.append(item)

    def checkout(self, title):
        item = self.find_by_title(title)
        if item:
            item.checkout()
        else:
            raise ValueError("Item not found.")

    def return_item(self, title):
        item = self.find_by_title(title)
        if item:
            item.return_item()
        else:
            raise ValueError("Item not found.")

    def find_by_title(self, title):
        for item in self.items:
            if item.title == title:
                return item
        return None

    def list_available(self):
        return [item for item in self.items if item.status == ItemStatus.AVAILABLE]


if __name__ == "__main__":
    db = Database("database.txt")
    library = Library()
    library.items = db.load_data()

    if not library.items:
        library.add_item(Book("Dune", ItemStatus.AVAILABLE, author="Frank Herbert", isbn="9780441172719"))
        library.add_item(Book("Pride and Prejudice", ItemStatus.AVAILABLE, author="Jane Austen", isbn="9780141439518"))
        library.add_item(DVD("Inception", ItemStatus.AVAILABLE, director="Christopher Nolan"))
        library.add_item(Magazine("National Geographic", ItemStatus.AVAILABLE, issue="March 2024"))
        db.save_items(library.items)

    print("All items:")
    for item in sorted(library.items):
        print(item)

    print("\nChecking out 'Dune'...")
dune = library.find_by_title("Dune")

if dune.status == ItemStatus.AVAILABLE:
    library.checkout("Dune")
    print(dune)
else:
    print(f"Dune is already {dune.status.value}.")

    print("\nAvailable items:")
    for item in library.list_available():
        print(item)

    db.save_items(library.items)
