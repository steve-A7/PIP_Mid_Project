'''This module contains utility classes and functions for the inventory and billing management application, including an IconManager for loading icons and a custom FloatSpinbox widget for handling float inputs with increment/decrement buttons. It also defines a list of predefined product categories for use in the inventory manager's dropdown menu.
'''
#All the library imports
import customtkinter as ctk
import os
from PIL import Image, ImageTk
#Helper class to load and scale icons from the assets folder
class IconManager:
    @staticmethod
    def load_icon(icon_name, size=(20, 20)) -> ctk.CTkImage | None: #default size is 20x20 pixels, can be overridden when calling the function
        # Construct path to assets folder
        asset_path = os.path.join(os.path.dirname(__file__), "assets", icon_name)
        #Attempt to load the icon image and return a CTKImage object, if missing or error occurs returns None
        try:
            if os.path.exists(asset_path):
                img = Image.open(asset_path)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            else:
                return None
        except Exception as e: #Log any errors that occur during icon loading and return None to prevent crashes due to missing icons
            print(f"Error loading icon {icon_name}: {e}")
            return None
#Custom widget for float input with increment/decrement buttons, used for stock quantity and discount fields in the inventory manager from https://customtkinter.tomschimansky.com/
class FloatSpinbox(ctk.CTkFrame):
    def __init__(self, *args, width: int = 150, height: int = 32, step_size: float = 1, **kwargs) -> None:
        super().__init__(*args, width=width, height=height, **kwargs)
        self.step_size = step_size
        self.configure(fg_color=("#3B3B3B", "#1A1A1A")) 
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.subtract_button = ctk.CTkButton(self, text="-", width=height-6, height=height-6,
                                               fg_color="#3b8ed0", hover_color="#36719f",
                                               command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)
        self.entry = ctk.CTkEntry(self, width=width-(2*height), height=height-6, 
                                  border_width=0, fg_color="transparent", justify="center")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.add_button = ctk.CTkButton(self, text="+", width=height-6, height=height-6,
                                            fg_color="#3b8ed0", hover_color="#36719f",
                                            command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)
        self.entry.insert(0, "0.0")
    #Function of adding 
    def add_button_callback(self) -> None:
        try:
            value = float(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return
    #Function of subtracting, with logic to prevent negative values which are not valid for stock quantity or discount percentage
    def subtract_button_callback(self) -> None:
        try:
            value = float(self.entry.get()) - self.step_size
            if value < 0: value = 0
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError: #Fallback
            return
    #Function to get current value
    def get(self) -> float:
        try:
            return float(self.entry.get())
        except ValueError: #Default to 0.0
            return 0.0
    #Function to set value programmatically, used for populating the fields when editing a product in the inventory manager
    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))
#predefined categories for dropdown in inventory manager
CATEGORIES = [
        "Fresh Produce (fruits & vegetables)", "Meat & Poultry", "Fish &Seafood", 
        "Dairy & Eggs", "Bakery & Bread", "Frozen Foods", 
        "Pantry Staples (rice, flour, oil, spices)", "Snacks & Confectionery", 
        "Beverages (soft drinks, juice, water, coffee, tea)", 
        "Health & Wellness (vitamins, supplements)", "Personal Care (soap, shampoo, skincare)", 
        "Household Essentials (cleaning supplies, paper goods)", 
        "Baby Products (diapers, formula, baby food)", "Pet Supplies", 
        "Electronics & Appliances", "Clothing & Apparel", 
        "Home & Kitchen (utensils, cookware, decor)", "Office & School Supplies", 
        "Seasonal & Outdoor (garden, holiday items, camping gear)"
    ]