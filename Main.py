#Michael Mocioiu 101569108
#Jason Gunawan 101465525
import tkinter as tk
from LibraryGUI import LibraryGUI
from LibraryManager import LibraryManager
lib = LibraryManager()
def main():
    root = tk.Tk()
    app = LibraryGUI(root, lib)
    root.mainloop()

if __name__ == "__main__":
    main()

