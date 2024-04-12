#Michael Mocioiu 101569108
#Jason Gunawan 101465525
from Book import Book

class Cart:
    def __init__(self):
        self.items = {}
    
    def clear(self):
        self.items = {}

    def add(self, book: Book):
        if book.id not in self.items:
            self.items[book.id] = book
        else:
            raise Exception("Book already in the cart!")
    
    def remove(self, id: int):
        if id in self.items:
            del self.items[id]
        else:
            raise Exception("Book not in cart!")

            