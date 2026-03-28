'''
This module defines the InventoryManager class, which is responsible for managing the products inventory in the application. It provides a user interface for viewing, adding, editing, and deleting products. The inventory data is loaded from and saved to a JSON file using the DataManager class. It uses utilities classes and predefined list. The InventoryManager also supports sorting and filtering of products based on various criteria such as category, stock level, and price.
'''
#All the library imports
import customtkinter as ctk
from tkinter import messagebox
from utilities import FloatSpinbox, CATEGORIES, IconManager

class InventoryManager(ctk.CTkFrame):
    #Initialization of the inventory manager frame and UI setup
    def __init__(self, parent, data_manager, update_callback):
        super().__init__(parent, fg_color="#494949", corner_radius=5)
        self.dm = data_manager #DataManager instance for loading and saving data
        self.update_callback = update_callback #Callback function to refresh billing view when inventory changes
        self.data = self.dm.load_data() #Load inventory data from JSON file
        # Variables for sorting, filtering, and tracking current edit item
        self.current_sort = "Product ID"
        self.current_filter = "All Categories"
        self.current_edit_item = None
        # Creating Main Containers
        self.list_view = ctk.CTkFrame(self, fg_color="transparent", corner_radius=5)
        self.form_view = ctk.CTkFrame(self, fg_color="#0a0a0a", corner_radius=5)
        self.setup_list_ui() #Setup the UI for the product list view
        self.setup_form_ui() #Setup the UI for the product form view (add/edit)
        self.show_list() #Show the product list view by default
    # Function to switch to list view and refresh the product list
    def show_list(self) -> None:
        self.form_view.pack_forget() 
        self.list_view.pack(fill="both", expand=True) 
        self.refresh_list()
    # Function to switch to form view for adding a new product or editing an existing product
    def show_form(self, item=None) -> None:
        self.current_edit_item = item
        self.list_view.pack_forget()
        self.form_view.pack(fill="both", expand=True, padx=50, pady=20)
        # Populate form fields if editing an existing product, otherwise clear fields for new product entry    
        for key, widget in self.form_entries.items():
            if key == "category":
                val = item[key] if item else CATEGORIES[0]
                widget.set(val)
            elif isinstance(widget, FloatSpinbox):
                val = item[key] if item else (0.0 if key == "discount" else 1.0)
                widget.set(val)
            else:
                widget.delete(0, "end")
                if item: widget.insert(0, str(item[key]))
        # Update form title based on whether adding a new product or editing an existing one
        self.form_title.configure(text="Edit Product" if item else "Add New Product")
    # Function to setup the UI components for the product list view, including header, filter/sort controls, and scrollable product list
    def setup_list_ui(self) -> None:
        # Header frame with title and add product button
        header = ctk.CTkFrame(self.list_view, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Inventory Management", image=IconManager.load_icon("inventory_icon.png", (28,28)), compound="left", anchor="center", font=("Caveat", 32, "bold")).pack(side="left")       
        ctk.CTkButton(header, text="Add Product", image=IconManager.load_icon("add_icon.png", (16,16)), font=("Poppins", 12), command=lambda: self.show_form(), 
                     fg_color="#1f538d", width=120).pack(side="right")
        # Controls frame for filter and sort options
        controls_frame = ctk.CTkFrame(self.list_view, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=5)
        # Filter dropdown
        ctk.CTkLabel(controls_frame, text="Filter:", font=("Poppins", 12)).pack(side="left", padx=(0, 5))
        self.filter_menu = ctk.CTkOptionMenu(
            controls_frame, 
            values=["All Categories"] + CATEGORIES,
            command=self.on_filter_change,
            width=220,
            fg_color="#1a1a1a",
            button_color="#333"
        )
        self.filter_menu.pack(side="left", padx=(0, 20))
        # Sort dropdown
        ctk.CTkLabel(controls_frame, text="Sort by:", font=("Poppins", 12)).pack(side="left", padx=(0, 5))
        self.sort_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["Product ID", "Item Name (A-Z)", "Item Name (Z-A)", "Stock (Low)", "Stock (High)", "Price (Low)", "Price (High)"],
            command=self.on_sort_change,
            width=160,
            fg_color="#1a1a1a",
            button_color="#333"
        )
        self.sort_menu.pack(side="left")
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_view, fg_color="#0a0a0a") # Scrollable frame for product list
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
    # Callback function for when filter option is changed, updates the current filter and refreshes the product list
    def on_filter_change(self, choice) -> None:
        self.current_filter = choice
        self.refresh_list()
    # Callback function for when sort option is changed, updates the current sort and refreshes the product list
    def on_sort_change(self, choice) -> None:
        self.current_sort = choice
        self.refresh_list()
    # Function to refresh the product list based on current filter and sort options, and render the product data in the scrollable frame
    def refresh_list(self) -> None:
        #Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        full_data = self.dm.load_data()
        products = full_data.get('products', [])
        #Apply Filtering & Sorting Logic
        if self.current_filter != "All Categories":
            products = [p for p in products if p['category'] == self.current_filter]
        sort_map = {
            "Product ID": lambda x: x['id'],
            "Item Name (A-Z)": lambda x: x['name'].lower(),
            "Item Name (Z-A)": lambda x: x['name'].lower(),
            "Stock (Low)": lambda x: x['stock'],
            "Stock (High)": lambda x: x['stock'],
            "Price (Low)": lambda x: x['price'],
            "Price (High)": lambda x: x['price']
        }
        is_reverse = "High" in self.current_sort or "(Z-A)" in self.current_sort #variable to determine if sorting should be in reverse order
        if self.current_sort in sort_map:
            products.sort(key=sort_map[self.current_sort], reverse=is_reverse)
        # Render Header Row
        W_ID, W_NAME, W_STOCK, W_PRICE, W_CAT, W_ACT = 80, 240, 80, 90, 440, 140
        h_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#1a1a1a", corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        headers = [("Product ID", W_ID), ("Item Name", W_NAME), ("Stock", W_STOCK), 
                   ("Price per Unit", W_PRICE), ("Category", W_CAT), ("Actions", W_ACT)]
        for text, width in headers:
            align = "center"
            lbl = ctk.CTkLabel(h_frame, text=text, width=width, font=("Manrope ExtraBold", 14), anchor=align)
            lbl.pack(side="left", padx=10, pady=5)
        #Render Each Product Row
        for i, item in enumerate(products):
            row_bg = "#7E7979" if i % 2 == 0 else "#58585A"
            f = ctk.CTkFrame(self.scrollable_frame, fg_color=row_bg, corner_radius=0, height=35)
            f.pack(fill="x", padx=5, pady=1)
            f.pack_propagate(False)
            is_low = item['stock'] <= 5 # Threshold for low stock
            stock_color = "#ff4444" if is_low else "#f1f1f1"
            stock_text = f"{item['stock']} (!)" if is_low else str(item['stock'])
            ctk.CTkLabel(f, text=item['id'], width=W_ID, font=("Poppins", 14), anchor="center").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=item['name'], width=W_NAME, font=("Poppins", 14), anchor="center").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=stock_text, width=W_STOCK, font=("Poppins", 14), anchor="center", text_color=stock_color).pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"৳{item['price']:.2f}", width=W_PRICE, font=("Poppins", 14), anchor="center").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=item['category'], width=W_CAT, anchor="center", font=("Poppins", 14)).pack(side="left", padx=10)
            #Edit & Delete Buttons
            btn_f = ctk.CTkFrame(f, fg_color="transparent")
            btn_f.pack(side="left", padx=5)
            ctk.CTkButton(btn_f, text="Edit", image=IconManager.load_icon("edit_icon.png", (12,12)), width=50, height=22, font=("Poppins", 14), fg_color="#66b4e2",
                         command=lambda i=item: self.show_form(i)).pack(side="left", padx=2)
            ctk.CTkButton(btn_f, text="Del", image=IconManager.load_icon("delete_icon.png", (12,12)), width=50, height=22, font=("Poppins", 14), fg_color="#C96A6A", hover_color="#C42525", 
                         command=lambda i=item: self.delete_product(i)).pack(side="left", padx=2)
    # Function to setup the UI components for the product form view, including input fields for product details and save/cancel buttons
    def setup_form_ui(self) -> None:
        self.form_title = ctk.CTkLabel(self.form_view, text="Add Product", font=("Poppins", 22, "bold"))
        self.form_title.pack(pady=20)
        # Container for form fields
        fields_container = ctk.CTkFrame(self.form_view, fg_color="transparent")
        fields_container.pack(pady=10)
        # Dictionary to hold references to form input widgets for easy access when saving product data
        self.form_entries = {}
        keys = [("name", "Item Name"), ("category", "Category"), ("stock", "Quantity"), 
                ("price", "Price per Unit"), ("description", "Description"), ("discount", "Discount %")]
        # Loop through each field definition and create corresponding input widget based on the field type
        for key, label in keys:
            ctk.CTkLabel(fields_container, text=label, font=("Poppins", 13)).pack(pady=(10, 0), anchor="w")
            if key == "category": #Category field uses a dropdown menu with predefined categories
                widget = ctk.CTkOptionMenu(fields_container, values=CATEGORIES, width=450, height=40,
                    fg_color="#a190eb", button_color="#9557e6", button_hover_color="#1f538d",
                    dropdown_fg_color="#1a1a1a", dropdown_hover_color="#333", dynamic_resizing=False)
                widget.pack(pady=5)
            elif key in ["stock", "discount"]: #Stock and Discount fields use a custom FloatSpinbox widget for numeric input with increment/decrement buttons
                widget = FloatSpinbox(fields_container, width=450, height=45)
                widget.pack(pady=5)
            else: #Other fields use a standard entry widget for text input
                widget = ctk.CTkEntry(fields_container, width=450, height=40, fg_color="#1a1a1a", border_color="#333")
                widget.pack(pady=5)
            self.form_entries[key] = widget
        # Save and Cancel Buttons
        btn_frame = ctk.CTkFrame(self.form_view, fg_color="transparent")
        btn_frame.pack(pady=40)
        ctk.CTkButton(btn_frame, text="Cancel", image=IconManager.load_icon("cancel_icon.png", (16,16)), font=("Poppins", 14), fg_color="#d8754e", width=140, height=40, command=self.show_list).pack(side="left", padx=15)
        ctk.CTkButton(btn_frame, text="Save Product", image=IconManager.load_icon("save_icon.png", (16,16)), font=("Poppins", 14), fg_color="#5fb68d", width=120, height=40, command=self.save_product).pack(side="left", padx=15)
    # Function to validate form input, save the product data to the JSON file, and refresh the product list view
    def save_product(self) -> None:
        # Validate input and save product data
        try:
            p_data = {key: widget.get() for key, widget in self.form_entries.items()}
            if not str(p_data['name']).strip(): #Item name is required and cannot be empty
                raise ValueError("Item Name is required.")
            try:
                p_data['stock'] = int(float(p_data['stock']))
                p_data['price'] = float(p_data['price'])
                if p_data['stock'] <= 0: raise ValueError("Stock quantity must be at least 1.") #Stock must be at least 1 to prevent adding out-of-stock items to inventory
                if p_data['price'] <= 0: raise ValueError("Price per unit must be greater than 0.") #Price must be greater than 0 to prevent free items in inventory
            except ValueError: #fallback for invalid numeric input in stock and price fields
                raise ValueError("Stock quantity and Price per unit must be valid numbers.")
            # Validate discount value and ensure it does not exceed 70%
            try:
                p_data['discount'] = float(p_data['discount'])
            except: #fallback to 0.0 if discount input is not given or invalid
                p_data['discount'] = 0.0
            #throw error if discount value is greater than 70%
            if p_data['discount'] > 70: raise ValueError("Discount cannot exceed 70%.")  
            # If editing an existing product, updates the product data in the list; otherwise, generates a new product ID and add the new product to the list
            if self.current_edit_item:
                idx = next(i for i, p in enumerate(self.data['products']) if p['id'] == self.current_edit_item['id'])
                p_data['id'] = self.current_edit_item['id']
                self.data['products'][idx] = p_data
            else:
                p_data['id'] = self.generate_product_id(p_data['category'], p_data['name'])
                self.data['products'].append(p_data)
            self.dm.save_data(self.data) #Save updated product data to JSON file
            self.update_callback() #Call the update callback to refresh the billing view in case any changes affect the billing process (e.g., stock changes)
            self.show_list() #Switch back to the product list view after saving the product      
        except ValueError as e: #Show error message if validation fails and prevent saving invalid product data
            messagebox.showerror("Validation Error", str(e))
    #Function doe auto generation of Product ID based on first letter of category and frst two letters of product name, followed by a 4-digit sequence number to ensure uniqueness
    def generate_product_id(self, category, name) -> str:
        prefix = f"{category[0].upper()}{name[:2].upper()}"
        count = sum(1 for p in self.data['products'] if p['id'].startswith(prefix)) + 1
        return f"{prefix}{count:04d}"
    #Function to delete a product from the inventory after confirming with the user, and refresh the product list and billing view accordingly
    def delete_product(self, item) -> None:
        if messagebox.askyesno("Confirm", f"Delete {item['name']}?"):
            self.data['products'] = [p for p in self.data['products'] if p['id'] != item['id']]
            self.dm.save_data(self.data)
            self.refresh_list()
            self.update_callback()