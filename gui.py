import tkinter as tk
from tkinter import ttk, messagebox
from logic import add_customer, get_customer, search_customer, create_invoices
from pdf_generator import generate_pdf
from datetime import date
import os

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Invoice Generator")
        self.root.geometry("800x700")
        self.root.configure(bg="white")

        # Mode selection
        mode_frame = tk.Frame(root, bg="white", pady=5)
        mode_frame.pack(fill="x", padx=20)
        self.mode_var = tk.StringVar(value="new")
        tk.Radiobutton(mode_frame, text="New Customer", variable=self.mode_var, value="new", bg="white", command=self.toggle_customer_mode).pack(side="left")
        tk.Radiobutton(mode_frame, text="Existing Customer", variable=self.mode_var, value="existing", bg="white", command=self.toggle_customer_mode).pack(side="left")

        # Customer detail frame (initially shown)
        self.customer_frame = tk.LabelFrame(root, text="Customer Details", padx=10, pady=10, bg="white", font=("Segoe UI", 10, "bold"))
        self.customer_frame.pack(padx=20, pady=10, fill="x")

        self.name_entry = self.create_labeled_entry(self.customer_frame, "Customer Name", 0)
        self.email_entry = self.create_labeled_entry(self.customer_frame, "Email", 1)
        self.phone_entry = self.create_labeled_entry(self.customer_frame, "Phone", 2)
        self.address_entry = self.create_labeled_entry(self.customer_frame, "Address", 3)

        tk.Button(self.customer_frame, text="Add Customer", command=self.save_customer).grid(row=4, column=0, columnspan=2, pady=10)

        # Existing customer frame (initially hidden)
        self.search_frame = tk.LabelFrame(root, text="Search & Select Customer", padx=10, pady=10, bg="white", font=("Segoe UI", 10, "bold"))

        tk.Label(self.search_frame, text="Search Customer", bg="white").grid(row=0, column=0, sticky="w")
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew", pady=2)
        self.search_entry.bind("<KeyRelease>", self.update_customer_dropdown)

        tk.Label(self.search_frame, text="Select Customer", bg="white").grid(row=1, column=0, sticky="w")
        self.customer_var = tk.StringVar()
        self.customer_menu = ttk.Combobox(self.search_frame, textvariable=self.customer_var)
        self.customer_menu.grid(row=1, column=1, sticky="ew", pady=2)
        self.search_frame.columnconfigure(1, weight=1)

        # Date field
        tk.Label(root, text="Date (YYYY-MM-DD)", bg="white").pack(padx=20, anchor="w")
        self.date_entry = tk.Entry(root)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))  # Auto-fill current date
        self.date_entry.pack(padx=20, fill="x", pady=(0, 10))

        # Items Frame
        items_frame = tk.LabelFrame(root, text="Items", padx=10, pady=10, bg="white", font=("Segoe UI", 10, "bold"))
        items_frame.pack(padx=20, fill="x")

        self.item_frame = tk.Frame(items_frame, bg="white")
        self.item_frame.pack(fill="x")
        self.items = []
        self.add_item_row()

        # Add item button
        tk.Button(root, text="Add More Item", command=self.add_item_row).pack(pady=5)

        # Paid checkbox
        self.paid_var = tk.BooleanVar(value=True)
        tk.Checkbutton(root, text="Paid", variable=self.paid_var, bg="white").pack(anchor="w", padx=20)

        # Generate invoice button
        tk.Button(root, text="Generate Invoice", command=self.generate_invoice, bg="#4CAF50", fg="white",
                  font=("Segoe UI", 10, "bold"), padx=10, pady=5).pack(pady=20)

    def create_labeled_entry(self, parent, label_text, row):
        tk.Label(parent, text=label_text, bg="white").grid(row=row, column=0, sticky="w")
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew", pady=2)
        parent.columnconfigure(1, weight=1)
        return entry

    def toggle_customer_mode(self):
        if self.mode_var.get() == "new":
            self.search_frame.pack_forget()
            self.customer_frame.pack(padx=20, pady=10, fill="x")
        else:
            self.customer_frame.pack_forget()
            self.search_frame.pack(padx=20, pady=10, fill="x")
            self.refresh_customers()

    def save_customer(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        if not name:
            messagebox.showerror("Error", "Name is required.")
            return

        add_customer(name, email, phone, address)
        messagebox.showinfo("Success", "Customer added.")
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.refresh_customers()

    def refresh_customers(self):
        customers = get_customer()
        self.customer_menu['values'] = [f"{cid} - {name}" for cid, name in customers]

    def update_customer_dropdown(self, event):
        keyword = self.search_entry.get()
        customers = search_customer(keyword) if keyword else get_customer()
        self.customer_menu['values'] = [f"{cid} - {name}" for cid, name in customers]

    def add_item_row(self):
        if not self.items:
            headers = ["Name", "Unit", "Qty", "Price (₹)"]
            for i, h in enumerate(headers):
                tk.Label(self.item_frame, text=h, bg="white").grid(row=0, column=i, padx=10, pady=2, sticky="ew")

        row = len(self.items) + 1
        name = tk.Entry(self.item_frame)
        unit = tk.Entry(self.item_frame)
        qty = tk.Entry(self.item_frame)
        price = tk.Entry(self.item_frame)

        name.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
        unit.grid(row=row, column=1, padx=10, pady=2, sticky="ew")
        qty.grid(row=row, column=2, padx=10, pady=2, sticky="ew")
        price.grid(row=row, column=3, padx=10, pady=2, sticky="ew")

        for i in range(4):
            self.item_frame.columnconfigure(i, weight=1)

        self.items.append((name, unit, qty, price))

    def generate_invoice(self):
        if self.mode_var.get() == "existing":
            selected = self.customer_var.get()
            if not selected:
                messagebox.showerror("Error", "Please select a customer.")
                return
            try:
                customer_id = int(selected.split(" - ")[0])
            except Exception:
                messagebox.showerror("Error", "Invalid customer format.")
                return
        else:
            messagebox.showerror("Error", "Switch to 'Existing Customer' to generate invoice.")
            return

        date_str = self.date_entry.get()
        items = []

        for code, unit, qty, price in self.items:
            try:
                if code.get() and unit.get() and int(qty.get()) and float(price.get()):
                    items.append((code.get(), unit.get(), int(qty.get()), float(price.get())))
            except ValueError:
                continue

        if not items:
            messagebox.showerror("Error", "Enter at least one valid item.")
            return

        invoice_id = create_invoices(customer_id, date_str, items)
        file = generate_pdf(invoice_id, f"invoice_{invoice_id}.pdf", paid=self.paid_var.get())
        messagebox.showinfo("Success", f"Invoice #{invoice_id} generated.")
        os.system(f"start {file}")


# To run the app from this file:
if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
