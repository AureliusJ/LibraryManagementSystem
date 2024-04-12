#Michael Mocioiu 101569108
#Jason Gunawan 101465525
class Book:
    next_id = 1000
    def __init__(self, title : str, author : str, category : str, quantity : int = 5, id: int = 0):
        self.id = id if id > 0 else Book.next_id
        self.title = title
        self.author = author
        self.category = category
        self.total_quantity = quantity
        self.available_quantity = quantity
        if id > 0:
            Book.next_id = id + 1
        else:
            Book.next_id += 1

    def isAvailable(self):
        return int(self.available_quantity) > 0

    def checkout(self):
        if self.available_quantity > 0:
            self.available_quantity -= 1
        else:
            raise Exception(f"There are not enough available copies of the book to lend!")
        
    def checkin(self):
        if self.available_quantity + 1 <= self.total_quantity:
            self.available_quantity += 1
        else:
            raise Exception(f"There are currrently no lent copies of this book!")
    
    def set_quantity(self, value: int):
        diff = value - self.total_quantity
        if diff >= 0 or self.available_quantity + diff >= 0:
            self.available_quantity += diff
            self.total_quantity = value
        else:
            raise Exception(f"There are not enough copies on hand (not lent) to lower the count to {value}")

    def to_dict(self):
        return {
            self.id: {
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "total_quantity": self.total_quantity,
            "available_quantity": self.available_quantity
            }
        }

    @classmethod
    def from_dict(cls, data):
        book_id, book_data = next(iter(data.items()))
        return cls(title=book_data["title"],
                   author=book_data["author"],
                   category=book_data["category"],
                   quantity=int(book_data.get("total_quantity", 5)),
                   id=int(book_id)
                )
