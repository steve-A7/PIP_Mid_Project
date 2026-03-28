'''
This module defines the BillingManager class, which provides the user interface and functional logics for managing the billing and invoicing system of the application. It allows users to search for products, add them to a cart, calculate totals with taxes and discounts, generate invoices, cancel cart, view invoice history, and export data to CSV. The module uses class and list from utilities module. The class interacts with the DataManager to load and save data, ensuring that stock levels are updated accordingly when items are added to the cart or when an invoice is finalized.
'''
#All the library imports
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from utilities import CATEGORIES, IconManager

class BillingManager(ctk.CTkFrame):
    #Initialization of the billing manager frame and UI setup
    def __init__(self, parent, data_manager) -> None:
        super().__init__(parent, fg_color="#000000")
        self.dm = data_manager # Store data manager reference
        self.cart_items = {}
        self.temp_stock = {} #Temporary storage for stock levels to prevent direct modification of master data until invoice is finalized
        self.history_visible = False # Track history visibility state
        self.current_filter = "All Categories" #Default filter for category dropdown
        self.setup_ui() #Setup the user interface components

    def setup_ui(self) -> None:
        #Left Panel: Product Search & List
        #left contauiner
        self.left_panel = ctk.CTkFrame(self, fg_color="#494949", corner_radius=5)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        #Header frame for title and icon
        header_f = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header_f.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(header_f, text="Billing & Invoice System", image=IconManager.load_icon("invoice_icon.png", (28,28)), compound="left", font=("Caveat", 32, "bold")).pack(side="left")
        #Control frame for search and filter options
        ctrl_f = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        ctrl_f.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(ctrl_f, text="Search Item by ID or Name:", 
                     font=("Poppins", 12)).pack(side="left", padx=(0, 10))
        self.search_var = ctk.StringVar() #Live search variable
        self.search_var.trace_add("write", lambda *args: self.update_search()) #Live search update on text change
        ctk.CTkEntry(ctrl_f, font=("Poppins", 12), textvariable=self.search_var, 
                     width=250, height=35).pack(side="left", padx=(0, 10)) #Search entry field
        self.filter_menu = ctk.CTkOptionMenu(ctrl_f, values=["All Categories"] + CATEGORIES,
                                             font=("Poppins", 12), command=self.on_filter_change, width=180, height=35,
                                             fg_color="#1a1a1a", button_color="#333")
        self.filter_menu.pack(side="left") #Category filter dropdown
        #Product list container
        self.product_list = ctk.CTkScrollableFrame(self.left_panel, fg_color="#0a0a0a")
        self.product_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Panel: Current Invoice,Actions & History
        #right container
        self.right_panel = ctk.CTkFrame(self, fg_color="#0d0d0d", width=420)
        self.right_panel.pack(side="right", fill="both", padx=(5, 10), pady=10)
        # Invoice Section
        self.invoice_container = ctk.CTkFrame(self.right_panel, fg_color="#494949", corner_radius=5)
        self.invoice_container.pack(fill="both", expand=True)
        ctk.CTkLabel(self.invoice_container, text="Current Invoice", font=("Poppins", 18)).pack(pady=10)
        self.cart_box = ctk.CTkTextbox(self.invoice_container, width=380, height=300, 
                                       fg_color="#111111", font=("Courier New", 11))
        self.cart_box.pack(padx=15, pady=5) #Cart textbox to display current items in the cart with details
        self.total_label = ctk.CTkLabel(self.invoice_container, text="Total: ৳0.00", 
                                        font=("Poppins", 20), text_color="#5fb68d")
        self.total_label.pack(pady=5)
        #Buttons
        btn_f = ctk.CTkFrame(self.invoice_container, fg_color="transparent")
        btn_f.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(btn_f, text="Generate Invoice", command=self.finalize_invoice, 
                     fg_color="#5fb68d", height=40, font=("Manrope ExtraBold", 20)).pack(fill="x", pady=5) #Generate invoice button to finalize current cart
        #Sub-Button frame for Cancel and Export options
        action_f = ctk.CTkFrame(btn_f, fg_color="transparent")
        action_f.pack(fill="x")
        ctk.CTkButton(action_f, text="Cancel Cart", command=self.clear_cart, 
                     fg_color="#d8754e", height=32, width=120, font=("Manrope ExtraBold", 16)).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(action_f, text="Export CSV", command=self.export_csv, 
                     fg_color="#1f538d", height=32, width=120, font=("Manrope ExtraBold", 16)).pack(side="left", expand=True, padx=2)
        # History Toggle Button
        self.hist_toggle_btn = ctk.CTkButton(self.invoice_container, text="View Invoice History ⬇", font=("Poppins", 14),
                                             command=self.toggle_history, fg_color="#1a1a1a", height=30)
        self.hist_toggle_btn.pack(fill="x", padx=15, pady=10)

        # History Frame (Initially hidden)
        self.history_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="#615959", 
                                                    label_text="Invoice History", label_font=("Manrope ExtraBold", 14),height=400)
        self.sync_temp_stock() #Load stock
        self.update_search() #Load Product List

    def sync_temp_stock(self) -> None:
        data = self.dm.load_data() #Load data
        self.temp_stock = {p['id']: p['stock'] for p in data.get('products', [])} #Copy stock to temporary storage for manipulating without affecting actual data

    def on_filter_change(self, choice) -> None:
        self.current_filter = choice #Update current filter based on dropdown selection
        self.update_search() #Refresh product list to apply new filter

    def update_search(self) -> None:
        for widget in self.product_list.winfo_children(): 
            widget.destroy() #Clear product list before repopulating with search results
        data = self.dm.load_data()
        products = data.get('products', [])
        query = self.search_var.get().lower() #Search text
        #Filter products based on search query and selected category
        filtered = [p for p in products if (query in p['name'].lower() or query in p['id'].lower())]
        #Filter by category if not "All Categories"
        if self.current_filter != "All Categories":
            filtered = [p for p in filtered if p['category'] == self.current_filter]
        #Render header row for product list
        W_ID, W_NAME, W_STOCK, W_PRICE, W_ACT = 80, 340, 80, 80, 50
        h_frame = ctk.CTkFrame(self.product_list, fg_color="#1a1a1a", height=30)
        h_frame.pack(fill="x", pady=(0, 5))
        for t, w in [("Product ID", W_ID), ("Item Name", W_NAME), ("Stock", W_STOCK), ("Price per Unit", W_PRICE), ("Add", W_ACT)]:
            ctk.CTkLabel(h_frame, text=t, width=w, font=("Manrope ExtraBold", 14)).pack(side="left", padx=5)
        #Render each product row with details and add button (adds to cart)
        for i, p in enumerate(filtered):
            row_bg = "#7E7979" if i % 2 == 0 else "#58585A"
            f = ctk.CTkFrame(self.product_list, fg_color=row_bg, corner_radius=0, height=35)
            f.pack(fill="x", pady=1); f.pack_propagate(False)
            current_qty = self.temp_stock.get(p['id'], 0)
            stock_color = "#ff4444" if current_qty <= 5 else "#ffffff"
            ctk.CTkLabel(f, text=p['id'], width=W_ID).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=p['name'], width=W_NAME).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=str(current_qty), width=W_STOCK, text_color=stock_color).pack(side="left", padx=5)
            ctk.CTkLabel(f, text=f"৳{p['price']:.0f}", width=W_PRICE).pack(side="left", padx=5)
            ctk.CTkButton(f, text="+", width=W_ACT, height=22, fg_color="#1f538d", 
                         command=lambda x=p: self.add_to_cart(x)).pack(side="left", padx=5)
    #Function to add selected item to cart, update temporary stock, and refresh accordingly
    def add_to_cart(self, product) -> None:
        pid = product['id']
        #Check if item is in stock before adding to cart
        if self.temp_stock[pid] <= 0:
            messagebox.showwarning("Out of Stock", f"{product['name']} is out of stock.")
            return
        #If in stock, add to cart and update temporary stock
        self.temp_stock[pid] -= 1
        if pid in self.cart_items:
            self.cart_items[pid]['qty'] += 1 #Increment quantity if already in cart
        else:
            self.cart_items[pid] = {'product': product, 'qty': 1} #Add new item to cart with quantity of 1
        self.refresh_cart_ui() #Refresh cart display to show updated items and totals
        self.update_search() #Refresh product list to update stock display after adding to cart
    #Function to clear the cart (restore stock levels and refreshes accordingly)
    def clear_cart(self) -> None:
        if not self.cart_items: return
        self.cart_items = {}
        self.sync_temp_stock()
        self.refresh_cart_ui()
        self.update_search()
        messagebox.showinfo("Cart Cleared", "Cart has been cancelled and stock restored.")
    #Function to refresh the cart UI (recalculate totals and updates display with current cart items and pricing details)
    def refresh_cart_ui(self) -> None:
        self.cart_box.delete("1.0", "end") #Clear textbox
        subtotal = 0
        # Header: Name, Qty, Original Price, Discount, Final Price
        header = f"{'Item':<15} {'Qty':<4} {'Orig':>7} {'Disc':>5} {'Total':>8}\n"
        self.cart_box.insert("end", header)
        self.cart_box.insert("end", f"{'-'*45}\n")
        # Iterate through cart items to calculate line totals and overall subtotal and display details
        for pid, data in self.cart_items.items():
            p = data['product']
            qty = data['qty']
            orig = p['price']
            disc_pct = p.get('discount', 0)
            # Calculations for discounted price and line total
            unit_discounted = orig * (1 - disc_pct/100)
            line_total = unit_discounted * qty
            subtotal += line_total
            #Display accordingly for each row
            name = p['name'][:14]
            self.cart_box.insert("end", f"{name:<15} {qty:<4} {orig:>7.0f} {int(disc_pct):>4}% ৳{line_total:>7.2f}\n")
        #Calculate VAT and Service Charge, then display the totals
        vat, sc = subtotal * 0.15, subtotal * 0.07
        total = subtotal + vat + sc
        #Display subtotal, VAT, Service Charge, and Grand Total in the cart textbox and update total label
        self.cart_box.insert("end", f"\n{'-'*45}\n")
        self.cart_box.insert("end", f"{'Subtotal:':<30} ৳{subtotal:>10.2f}\n")
        self.cart_box.insert("end", f"{'VAT (15%):':<30} ৳{vat:>10.2f}\n")
        self.cart_box.insert("end", f"{'Service (7%):':<30} ৳{sc:>10.2f}\n")
        self.cart_box.insert("end", f"{'Grand Total:':<30} ৳{total:>10.2f}")
        self.total_label.configure(text=f"Total: ৳{total:.2f}")
    #Function to finalize the invoice (generate invoice data, update stock levels in master data, save invoice, and reset cart)
    def finalize_invoice(self) -> None:
        #Prevent finalizing if cart is empty
        if not self.cart_items: 
            return
        data = self.dm.load_data()
        inv_count = len(data.get('invoices', []))
        inv_id = f"#INV0x{inv_count + 1:04X}" #Auto generate invoice ID based on count of existing invoices (hex format)
        # Apply temporary stock to permanent master data
        for p in data['products']:
            if p['id'] in self.temp_stock:
                p['stock'] = self.temp_stock[p['id']]
        #Create new invoice entry with details and save to data manager
        new_invoice = {
            "invoice_no": inv_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),  #Timestamp for invoice generation
            "items": [f"{v['qty']}x {v['product']['name']}" for v in self.cart_items.values()],
            "total": self.total_label.cget('text').replace("Total: ৳", "")
        }
        #Save invoice to data manager
        if 'invoices' not in data: 
            data['invoices'] = []
        data['invoices'].append(new_invoice)
        
        self.dm.save_data(data)
        self.cart_items = {}
        self.sync_temp_stock()
        self.refresh_cart_ui()
        self.update_search()
        if self.history_visible: 
            self.refresh_history_ui() #Refresh history view if currently visible to show new invoice
        messagebox.showinfo("Success", f"Invoice {inv_id} generated successfully!") #Show success message with generated invoice ID
    #Function for toggling visibility of invoice history section
    def toggle_history(self) -> None:
        if not self.history_visible:
            # Show History
            self.history_frame.pack(fill="both", expand=True, pady=5)
            self.refresh_history_ui()
            self.hist_toggle_btn.configure(text="Hide Invoice History ⬆", font=("Poppins", 14), fg_color="#333")
            self.history_visible = True
        else:
            # Hide History
            self.history_frame.pack_forget()
            self.hist_toggle_btn.configure(text="View Invoice History ⬇", font=("Poppins", 14), fg_color="#1a1a1a")
            self.history_visible = False
    #Function to refresh the invoice history UI (re-render the list of past invoices with details)
    def refresh_history_ui(self) -> None:
        # Clear existing rows
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        data = self.dm.load_data()
        invoices = data.get('invoices', [])[::-1] #show latest first
        #Render invoice data from master data
        for inv in invoices:
            f = ctk.CTkFrame(self.history_frame, fg_color="#111")
            f.pack(fill="x", pady=5, padx=5) 
            ctk.CTkLabel(f, text=f"{inv['invoice_no']} | {inv['date']}", 
                         font=("Poppins", 14), anchor="w").pack(fill="x", padx=10, pady=(5, 0))            
            ctk.CTkLabel(f, text=f"Amount: ৳{inv['total']}", 
                         text_color="#5fb68d", font=("Poppins", 14),anchor="w").pack(fill="x", padx=10, pady=(0, 5))
    #Function to export invoice history into CSV file format
    def export_csv(self) -> None:
        data = self.dm.load_data()
        invoices = data.get('invoices', [])
        if invoices:
            self.dm.export_to_csv(invoices, "invoice_history.csv", ["invoice_no", "date", "items", "total"])
            messagebox.showinfo("Export Success", "Invoice history exported successfully to 'invoice_history.csv'") #Show success message after exporting