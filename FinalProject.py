#Michael Mocioiu 101459108
#Jason Gunawan 101465525
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
import json
import os

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
    

class LibraryGUI:
    def __init__(self, master, library_manager : LibraryManager):
        self.master = master
        self.master.title("Library Management System")
        self.master.geometry("1060x800")
        self.master.resizable(False, False)
        self.lib_mgr = library_manager
        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        self.main_frame = ttk.Frame(self.master, borderwidth=5, relief="ridge", width=400, height=300)
        self.main_frame.pack(expand=True, fill="both")

        # Search form-----------------
        ttk.Label(self.main_frame, text="Search (click a row to select)",font=("Arial", 11, "bold")).grid(row=0, column=0)
        self.search_frame = ttk.Frame(self.main_frame,  borderwidth=5, relief="ridge", width=400, height=300)
        self.search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.search_frame, text="Title:").grid(row=0, column=0)
        self.search_title_entry = tk.Entry(self.search_frame)
        self.search_title_entry.grid(row=1, column=0)

        ttk.Label(self.search_frame, text="Author:").grid(row=0, column=1)
        self.search_author_entry = tk.Entry(self.search_frame)
        self.search_author_entry.grid(row=1, column=1)

        ttk.Label(self.search_frame, text="Category:").grid(row=0, column=2)
        self.search_category_entry = tk.Entry(self.search_frame)
        self.search_category_entry.grid(row=1, column=2)


        ttk.Label(self.search_frame, text="Only Show Available:").grid(row=0, column=3)
        self.available_var = tk.BooleanVar(value=False)
        self.available_cbox = ttk.Checkbutton(self.search_frame, variable=self.available_var)
        self.available_cbox.grid(row=1, column=3)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.update_tree_view)
        self.search_button.grid(row=0, column=4, rowspan=2)


        #Results display--------------------
        self.tree_frame = ttk.Frame(self.search_frame, width=60, height=100)
        self.tree_frame.grid(row=2, column=0, columnspan=5)

        self.tree = ttk.Treeview(self.tree_frame, selectmode="browse", columns=("Title", "Author", "Category", "Total Quantity", "Available Quantity"), height=15)
        self.tree.heading("#0", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Total Quantity", text="Total Quantity")
        self.tree.heading("Available Quantity", text="Available Quantity")
        self.tree.column("#0", width=50)
        self.tree.column("Title", width=200)
        self.tree.column("Author",width=150)
        self.tree.column("Category", width=150)
        self.tree.column("Total Quantity", width=100)
        self.tree.column("Available Quantity", width=110)
        self.tree.tag_configure('grey', background='#cccccc')
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)
        self.tree.pack(side="left", pady=20, padx=10, expand=True)
        self.tree_scrlbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree_scrlbar.pack(side="left", pady=20, fill="both")
        self.tree.configure(xscrollcommand=self.tree_scrlbar.set)
        

        #Cart --------------------------------
        ttk.Label(self.main_frame, text="Cart (click to select)",font=("Arial", 11, "bold")).grid(row=0, column=1)
        self.cart_frame = ttk.Frame(self.main_frame, borderwidth=5, relief="ridge", width=200, height=300)
        self.cart_frame.grid(row=1, column=1, rowspan=1, columnspan=1,  padx=10, pady=10, sticky="nsew")

        self.checkout_cart_button = tk.Button(self.cart_frame, text="Check Out", command=self.checkout_cart)
        self.checkout_cart_button.grid(row=0, column=0, sticky="nsew")

        self.remove_cart_button = tk.Button(self.cart_frame, text="Remove Selected", command=self.remove_from_cart)
        self.remove_cart_button.grid(row=0, column=1, sticky="nsew")

        self.cart_select_list = tk.Listbox(self.cart_frame, height=20, width=30)
        self.cart_select_list.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

        #Book Details Frame ------------------------------
        self.book_frame = ttk.Frame(self.main_frame, borderwidth=5, width=1040, relief="ridge")
        self.book_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")


        ttk.Label(self.book_frame, text="Book Details",font=("Arial", 11, "bold")).pack(side="top", fill="x", expand=True, padx=5)

        self.edit_form_frame = ttk.Frame(self.book_frame, borderwidth=5, relief="ridge")
        self.edit_form_frame.pack(side="top", fill="x", expand=True)
        self.edit_form_frame.grid_rowconfigure(0, weight=1)
        self.edit_form_frame.grid_rowconfigure(1, weight=1)
        self.edit_form_frame.grid_columnconfigure(0, weight=1)
        self.edit_form_frame.grid_columnconfigure(1, weight=1)
        self.edit_form_frame.grid_columnconfigure(2, weight=1)
        self.edit_form_frame.grid_columnconfigure(3, weight=1)


        self.selection_id :int
        ttk.Label(self.edit_form_frame, text="Title:").grid(row=1, column=0, padx=10, pady=5)
        self.edit_title_entry = tk.Entry(self.edit_form_frame, state='readonly')
        self.edit_title_entry.grid(row=2, column=0, padx=10, pady=15)

        ttk.Label(self.edit_form_frame, text="Author:").grid(row=1, column=1, padx=10, pady=5)
        self.edit_author_entry = tk.Entry(self.edit_form_frame, state='readonly')
        self.edit_author_entry.grid(row=2, column=1, padx=10, pady=15)

        ttk.Label(self.edit_form_frame, text="Category:").grid(row=1, column=2, padx=10, pady=5)
        self.edit_category_entry = tk.Entry(self.edit_form_frame, state='readonly')
        self.edit_category_entry.grid(row=2, column=2, padx=10, pady=15)

        ttk.Label(self.edit_form_frame, text="Total Quantity:").grid(row=1, column=3, padx=10, pady=5)
        self.edit_total_quantity_entry = tk.Spinbox(self.edit_form_frame, state='disabled', from_=0, to=999, increment=1, wrap=True)
        self.edit_total_quantity_entry.grid(row=2, column=3, padx=10, pady=15)

        self.edit_buttons_frame = ttk.Frame(self.book_frame, borderwidth=5, relief="ridge")
        self.edit_buttons_frame.pack(side="top", fill="x", expand=True)

        self.edit_buttons_frame.grid_rowconfigure(0, weight=1)
        self.edit_buttons_frame.grid_columnconfigure(0, weight=1)
        self.edit_buttons_frame.grid_columnconfigure(1, weight=1)
        self.edit_buttons_frame.grid_columnconfigure(2, weight=1)
        self.edit_buttons_frame.grid_columnconfigure(3, weight=1)


        self.toggle_edit_button = tk.Button(self.edit_buttons_frame, text="  Edit  ", state="disabled", command=self.toggle_edit_mode)
        self.toggle_edit_button.grid(row=0, column=0, sticky="nsew", padx=5)

        self.borrow_button = tk.Button(self.edit_buttons_frame, text="Add To Cart", state="disabled", command=self.add_to_cart)
        self.borrow_button.grid(row=0, column=1, sticky="nsew", padx=5)

        self.return_button = tk.Button(self.edit_buttons_frame, text="Check In", state="disabled", command=self.checkin_book)
        self.return_button.grid(row=0, column=2, sticky="nsew", padx=5)

        self.remove_button = tk.Button(self.edit_buttons_frame, text="Remove Book", state="disabled", command=self.remove_book)
        self.remove_button.grid(row=0, column=3, sticky="nsew", padx=5)

        self.confirm_edit_button = tk.Button(self.edit_buttons_frame, text="Confirm", command=self.edit_book)
        self.update_tree_view()

        #Add book frame------------------------------------------
        self.add_book_frame = ttk.Frame(self.main_frame, borderwidth=5, relief="ridge", width=1040, height=300)
        self.add_book_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.add_book_frame.grid_rowconfigure(0, weight=1)
        self.add_book_frame.grid_rowconfigure(1, weight=1)
        self.add_book_frame.grid_rowconfigure(2, weight=1)
        self.add_book_frame.grid_rowconfigure(3, weight=1)
        self.add_book_frame.grid_columnconfigure(0, weight=1)
        self.add_book_frame.grid_columnconfigure(1, weight=1)
        self.add_book_frame.grid_columnconfigure(2, weight=1)
        self.add_book_frame.grid_columnconfigure(3, weight=1)
        ttk.Label(self.add_book_frame, text="Add Book:",font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=4)

        ttk.Label(self.add_book_frame, text="Title:").grid(row=1, column=0, padx=10, pady=5)
        self.add_title_entry = tk.Entry(self.add_book_frame)
        self.add_title_entry.grid(row=2, column=0, padx=10, pady=5)

        ttk.Label(self.add_book_frame, text="Author:").grid(row=1, column=1, padx=10, pady=5)
        self.add_author_entry = tk.Entry(self.add_book_frame)
        self.add_author_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_frame, text="Category:").grid(row=1, column=2, padx=10, pady=5)
        self.add_category_entry = tk.Entry(self.add_book_frame)
        self.add_category_entry.grid(row=2, column=2, padx=10, pady=5)

        ttk.Label(self.add_book_frame, text="Total Quantity:").grid(row=1, column=3, padx=10, pady=5)
        self.add_total_quantity_entry = tk.Spinbox(self.add_book_frame, from_=0, to=999, increment=1, wrap=True)
        self.add_total_quantity_entry.delete(0, tk.END)
        self.add_total_quantity_entry.insert(0, 5)
        self.add_total_quantity_entry.grid(row=2, column=3, padx=10, pady=5)

        self.add_book_button = tk.Button(self.add_book_frame, text="Add Book", command=self.add_book)
        self.add_book_button.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

    def search(self):
        title = self.search_title_entry.get().strip()
        author = self.search_author_entry.get().strip()
        category = self.search_category_entry.get().strip()
        results = []
        final_results = []
        if title:
            title_results = self.lib_mgr.search("title", title)
            results.append(title_results)
        if author:
            author_results = self.lib_mgr.search("author", author)
            results.append(author_results)
        if category:
            category_results = self.lib_mgr.search("category", category)
            results.append(category_results)

        #handle blank search to return all books
        if not title and not author and not category:
            final_results = self.lib_mgr.get_book_list()
        else:
            #Filter out any entries that do not occur in all searches
            if results:
                final_results = results[0]
                for r in results[1:]:
                    final_results = [book for book in final_results if book in r]

        #filter out any books that are not available
        if self.available_var.get():
            for i,item in enumerate(final_results):
                if not item.isAvailable():
                    final_results.pop(i)
        return final_results

    def update_tree_view(self):
        # Clear existing entries in the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        results = self.search()
        for index, book in enumerate(results):
            tag = "" if index % 2 == 0 else "grey"
            self.tree.insert("", "end", text=str(book.id), values=(book.title, book.author, book.category, book.total_quantity, book.available_quantity), tags=(tag,))

    def update_cart_view(self):
        self.cart_select_list.delete(0, "end")
        cart = self.lib_mgr.cart.items
        for book in cart.values():
            self.cart_select_list.insert("end", f"{book.id}: {book.title}")

    def borrow_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            book_data = item['values']
            # Your logic for borrowing a book using book_data goes here

    def return_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            book_data = item['values']
            # Your logic for returning a book using book_data goes here

    def toggle_edit_mode(self):
        if self.edit_title_entry['state'] == 'readonly':
            self.enable_edit_inputs()
            self.toggle_edit_button.config(text="Cancel")
            self.borrow_button.grid_remove()
            self.confirm_edit_button.grid(row=0, column=1, sticky="nsew", padx=5)
            self.return_button.config(state="disabled")
            self.remove_button.config(state="disabled")
        else:
            self.disable_edit_inputs()
            self.toggle_edit_button.config(text="Edit")
            self.confirm_edit_button.grid_remove()
            self.borrow_button.grid(row=0, column=1,sticky="nsew", padx=5)
            self.return_button.config(state="normal")
            self.remove_button.config(state="normal")

    def edit_book(self):
        id = int(self.selection_id)
        title = self.edit_title_entry.get().strip()
        author = self.edit_author_entry.get().strip()
        category = self.edit_category_entry.get().strip()
        quantity = self.edit_total_quantity_entry.get()
        try:
            self.lib_mgr.edit_book(int(id), title, author, category, int(quantity))
            self.toggle_edit_mode()
            self.update_tree_view()
        except Exception as e:
            self.show_error(str(e))

    def on_tree_select(self, event):
        if self.edit_title_entry['state'] == 'normal':
            self.toggle_edit_mode()
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            self.selection_id = int(item['text'])
            self.populate_edit_form()

    def populate_edit_form(self):
        book = self.lib_mgr.get_book_by_id(self.selection_id)
        self.clear_edit_form()
        self.enable_edit_inputs()
        self.edit_title_entry.insert(0, book.title)
        self.edit_author_entry.insert(0, book.author)
        self.edit_category_entry.insert(0, book.category)
        self.edit_total_quantity_entry.insert(0, book.total_quantity)
        self.disable_edit_inputs()
        self.toggle_edit_button.config(state="normal")
        self.borrow_button.config(state="normal")
        self.return_button.config(state="normal")
        self.remove_button.config(state="normal")

    def clear_edit_form(self):
        self.enable_edit_inputs()
        self.edit_title_entry.delete(0, tk.END)
        self.edit_author_entry.delete(0, tk.END)
        self.edit_category_entry.delete(0, tk.END)
        self.edit_total_quantity_entry.delete(0, tk.END)
        self.disable_edit_inputs()
        self.toggle_edit_button.config(state="disabled")
        self.borrow_button.config(state="disabled")
        self.return_button.config(state="disabled")
        self.remove_button.config(state="disabled")



    def enable_edit_inputs(self):
        self.edit_title_entry.config(state='normal')
        self.edit_author_entry.config(state='normal')
        self.edit_category_entry.config(state='normal')
        self.edit_total_quantity_entry.config(state='normal')

    def disable_edit_inputs(self):
        self.edit_title_entry.config(state='readonly')
        self.edit_author_entry.config(state='readonly')
        self.edit_category_entry.config(state='readonly')
        self.edit_total_quantity_entry.config(state='disabled')
            
    def show_error(self, message : str="An error occurred"):
        messagebox.showerror("Error", message)

    def add_to_cart(self):
        if self.selection_id:
            try:
                self.lib_mgr.add_to_cart(int(self.selection_id))
                self.update_cart_view()
            except Exception as e:
                self.show_error(e)

    def remove_from_cart(self):
        id = self.cart_select_list.get(self.cart_select_list.curselection()[0]).split(": ")[0]
        if id:
            book = self.lib_mgr.get_book_by_id(int(id))
            if book:
                try:
                    self.lib_mgr.remove_from_cart(book.id)
                    self.clear_edit_form()
                    self.update_cart_view()
                except Exception as e:
                    self.show_error(e)

    def checkout_cart(self):
        reciept_text: str = self.lib_mgr.generate_reciept()
        self.lib_mgr.cart_checkout()
        self.update_cart_view()
        self.update_tree_view()
        print(self.selection_id)
        self.populate_edit_form()
        messagebox.askyesno("Reciept", f"{reciept_text}\n\nWould you like to print the reciept?")


    def checkin_book(self):
        try:
            self.lib_mgr.check_in_book(self.selection_id)
            self.update_tree_view()
        except Exception as e:
            self.show_error(e)

    def add_book(self):
        title = self.add_title_entry.get().strip().title()
        author = self.add_author_entry.get().strip().title()
        category = self.add_category_entry.get().strip().title()
        quantity = int(self.add_total_quantity_entry.get())
        if not (title and author and category):
            self.show_error("All fields must have an input!")
        else:
            try:
                self.lib_mgr.add_book(title, author, category, quantity)
                self.update_tree_view()
                self.add_title_entry.delete(0, tk.END)
                self.add_author_entry.delete(0, tk.END)
                self.add_category_entry.delete(0, tk.END) 
                self.add_total_quantity_entry.delete(0, tk.END)
                self.add_total_quantity_entry.insert(0, 5)
            except Exception as e:
                self.show_error(e)

    def remove_book(self):
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this book?"):
            try:
                self.lib_mgr.remove_book(self.selection_id)
                self.clear_edit_form()
                self.update_tree_view()
            except Exception as e:
                self.show_error(e)


lib = LibraryManager()
def main():
    root = tk.Tk()
    app = LibraryGUI(root, lib)
    root.mainloop()

if __name__ == "__main__":
    main()