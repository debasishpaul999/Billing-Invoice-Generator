from db import create_tables
from gui import InvoiceApp
import tkinter as tk

def main():
    create_tables()
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
