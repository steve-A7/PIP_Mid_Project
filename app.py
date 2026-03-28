'''
This module defines the main application class for the Inventory & Billing System, which sets up the user interface and manages the navigation between the inventory management and billing views. It initializes the data manager, creates the sidebar with navigation buttons, and contains methods to refresh the billing view and switch between views.
'''
#All the library imports
import customtkinter as ctk
from data_manager import DataManager
from inventory_manager import InventoryManager
from billing_manager import BillingManager
from utilities import IconManager

class App(ctk.CTk):
    # Main application class that initializes the UI and manages view navigation
    def __init__(self):
        super().__init__()
        self.title("Inventory & Billing System")
        self.geometry("1600x1050")
        self.iconbitmap(r'./assets/app_icon.ico')
        ctk.set_appearance_mode("dark") 
        # Load data manager
        self.dm = DataManager()
        # Layout: Sidebar & Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=5, fg_color="#050505")
        self.sidebar.grid(row=0, column=0, sticky="nsew") 
        ctk.CTkLabel(self.sidebar, text=" Dashboard", fg_color="#757575", image=IconManager.load_icon("dashboard_icon.png", (16,16)), compound="left", font=("Century Gothic", 22, "bold"), text_color="#77b1f3").pack(fill="x", padx=5,pady=30)
        # Sidebar Buttons to switch between Inventory and Billing views, with active state indication
        self.btn_inv = ctk.CTkButton(self.sidebar, text="Inventory", image=IconManager.load_icon("inventory_icon.png", (14,14)), compound="left", font=("Epilogue", 14),
                                     fg_color="transparent", anchor="w",
                                     hover_color="#555555", height=45,
                                     command=lambda: self.show_view("inv"))
        self.btn_inv.pack(fill="x", padx=10, pady=5)
        self.btn_bill = ctk.CTkButton(self.sidebar, text="Billing & Invoice", image=IconManager.load_icon("invoice_icon.png", (14,14)), compound="left", font=("Epilogue", 14),
                                      fg_color="transparent", anchor="w",
                                      hover_color="#555555", height=45,
                                      command=lambda: self.show_view("bill"))
        self.btn_bill.pack(fill="x", padx=10, pady=5)
        # Main Views
        self.container = ctk.CTkFrame(self, fg_color="#363636", corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        # Initialize both views but only show the inventory view by default; the billing view will be updated with the latest data when switched to
        self.view_inv = InventoryManager(self.container, self.dm, self.refresh_billing)
        self.view_bill = BillingManager(self.container, self.dm)
        # Show inventory view by default
        self.show_view("inv")
    #Function for refreshing billing view
    def refresh_billing(self):
        self.view_bill.update_search()
    #FUnction to switch between inventory and billing views, with logic to toggle the visibility of the views and update the active state of the sidebar buttons
    def show_view(self, view_name):
        self.view_inv.pack_forget()
        self.view_bill.pack_forget()
        if view_name == "inv":
            self.view_inv.pack(fill="both", expand=True)
            self.btn_inv.configure(fg_color="#292828") # Active indicator
            self.btn_bill.configure(fg_color="transparent")
        else:
            self.view_bill.pack(fill="both", expand=True)
            self.btn_bill.configure(fg_color="#292828")
            self.btn_inv.configure(fg_color="transparent")

