#Michael Mocioiu 101569108
#Jason Gunawan 101465525
from Book import Book
from datetime import datetime, timedelta
from Cart import Cart
import json
import os

class LibraryManager:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    books_file_path = os.path.join(script_dir, "BookData.json")
    def __init__(self):
        self.books = {}
        self.cart = Cart()
        self.read_from_file()

    def get_books_json(self):
        out_dict = {}
        for book in self.books.values():
            out_dict.update(book.to_dict())
        return out_dict

    def write_to_file(self):
        if not os.path.exists(LibraryManager.books_file_path):
            with open(LibraryManager.books_file_path, "w") as file:
                file.write("{}") 
        with open(LibraryManager.books_file_path, "w") as file:
            json.dump(self.get_books_json(), file)

    def read_from_file(self):
        if not os.path.exists(LibraryManager.books_file_path):
            return 
        with open(LibraryManager.books_file_path, "r") as file:
            data = json.load(file)
            for id, book_data in data.items():
                book = Book.from_dict({id: book_data})
                self.books[book.id] = book

    #Book management methods
    def add_book(self, title: str, author: str, category: str, quantity: int):
        for book in self.books.values():
            if book.title == title and book.author == author:
                raise Exception("A book with the same title and author already exists.")
        book: Book = Book(title, author, category, quantity)
        self.books[book.id] = book
        self.write_to_file()
            
    
    def remove_book(self, id: int):
        if id in self.books:
            book: Book = self.books[id]
            if book.total_quantity == book.available_quantity:
                del self.books[id]
                self.write_to_file()
                Book.next_id = list(self.books.keys())[-1] + 1
            else:
                raise Exception("Cannot remove books from the catalogue while some copies are lent!")

        
    def search(self, criteria : str, value : str):
        results = []
        for book in self.books.values():
            if value.lower() in getattr(book, criteria).lower():
                results.append(book)
        return results
    

    def get_book_list(self):
        books = []
        for book in self.books.values():
            books.append(book)
        return books

    def get_book_by_id(self, id: int):
        if id in self.books.keys():
            return self.books[id]
        else:
            raise Exception("Book not found!")
    
    def get_book_by_title_author(self, title: str, author: str):
        for book in self.books.values():
            if book.title == title and book.author == author:
                return book
            


    def edit_book(self, id: int, title: str, author: str, category: str, total_quantity: int):
        book: Book = self.get_book_by_id(id)
        title = title.title()
        author = author.title()
        category = category.title()
        
        if total_quantity < book.total_quantity - book.available_quantity:
            raise Exception("There are not enough available copies in the system to remove that many!")
            
        book.title = title
        book.author = author
        book.category = category
        book.set_quantity(total_quantity)

        
    def check_in_book(self, id: int):
        book: Book = self.get_book_by_id(id)
        try:
            book.checkin()
        except Exception as e:
            raise e

    #Cart methods
    def add_to_cart(self, id: int):
        try:
            book: Book = self.get_book_by_id(id)
            if book.available_quantity > 0:
                self.cart.add(book)
            else:
                raise Exception("All copies of this book are currently checked out!")
        except Exception as e:
            raise e
    
    def remove_from_cart(self, id: int):
        try:
            self.cart.remove(id)
        except Exception as e:
            raise e
        
    def checkout_book(self, id: int):
        if id in self.books:
            if self.books[id].available_quantity > 0:
                print(self.books[id])
                self.books[id].checkout()
    
    def cart_checkout(self):
        if (len(self.cart.items) != 0):
            for entry in self.cart.items.items():
                self.checkout_book(entry[0])
            self.cart.clear()
        else:
            raise Exception("Cart is empty!")

    #Transactions
    def generate_reciept(self):
        date = datetime.now()
        out: str = ""
        out += f"\nDate Borrowed: {date.strftime('%d-%m-%Y')}\n"
        out += f"Due by: {(date + timedelta(days=30)).strftime('%d-%m-%Y')}\n\nBooks:\n"
        for item in self.cart.items.values():
            out += f"    {item.title} - {item.author}\n"
        return out

