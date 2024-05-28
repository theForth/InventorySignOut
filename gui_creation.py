import tkinter as tk
from tkinter import ttk, messagebox
import phonenumbers
import datetime

##WIDGETS##
class SharedWidgets:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # --- Widgets for Name, Date, Phone Number --- 
        tk.Label(self.master, text="Name (First Last):").grid(row=0, column=0, sticky="e")
        self.user_name_entry = tk.Entry(self.master)
        self.user_name_entry.grid(row=0, column=1, sticky="w")

        tk.Label(self.master, text="Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.date_label = tk.Label(self.master, text=datetime.date.today())
        self.date_label.grid(row=1, column=1, padx=5, pady=5)

        # Phone Number Entry (with formatting)
        def format_phone_number(event=None):  # Define format_phone_number inside
            current = self.phone_number_entry.get().replace("-", "")  # Use self.phone_number_entry
            try:
                # formatted = phonenumbers.format_number(phonenumbers.parse(current, "US"), phonenumbers.PhoneNumberFormat.NATIONAL) if current else ""
                formatted = "".join([i + "-" if (j + 1) % 3 == 0 and j != 8 else i for j, i in enumerate(current)])

            except phonenumbers.NumberParseException:
                formatted = current
            self.phone_number_entry.delete(0, tk.END)
            self.phone_number_entry.insert(0, formatted)
            return True  # Validation successful
        tk.Label(self.master, text="Phone Number (XXX-XXX-XXXX):").grid(row=2, column=0, sticky="e")
        self.phone_number_entry = tk.Entry(self.master)
        self.phone_number_entry.grid(row=2, column=1, sticky="w")
        self.phone_number_entry.bind("<KeyRelease>", format_phone_number)  # Use self.phone_number_entry

class AccessCardWidgets(SharedWidgets):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self.master, text="Card Number:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.card_number_entry = tk.Entry(self.master)
        self.card_number_entry.grid(row=4, column=1, padx=5, pady=5)

class KeyWidgets(SharedWidgets):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self.master, text="Key Name:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.key_name_entry = tk.Entry(self.master)
        self.key_name_entry.grid(row=4, column=1, padx=5, pady=5)

class EquipmentWidgets(SharedWidgets):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self.master, text="Item Type:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.item_type_combobox = ttk.Combobox(self.master, values=["Laptop", "Projector", "Camera", "Other"])
        self.item_type_combobox.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Item Details:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.item_details_entry = tk.Entry(self.master)
        self.item_details_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Button(self.master, text="Add", command=self.add_equipment_to_listbox).grid(row=6, column=1, padx=5, pady=5)

        # Equipment Listbox (with multiple selection)
        self.equipment_listbox = tk.Listbox(self.master, selectmode=tk.MULTIPLE)
        self.equipment_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

    def add_equipment_to_listbox(self):
        """Adds the selected item and details to the equipment listbox."""
        current_tab = self.tabs.tab(self.tabs.select(), "text")
        if current_tab in self.subtab_widgets:
            listbox = self.subtab_widgets[current_tab]["equipment_listbox"]

            item_type = self.item_type_combobox.get()
            item_details = self.item_details_entry.get()

            if item_type and item_details:
                display_text = f"{item_type} - {item_details}"
                listbox.insert(tk.END, display_text)
                self.item_details_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Missing Information", "Please select an item type and enter details.")

class GUICreation:
    def __init__(self, master):
        self.master = master
    def create_sign_out_subtab(self, category):
        """Creates the "Sign Out" subtab for a category."""
        sign_out_frame = ttk.Frame(self.master)

        # --- Dynamically create fields based on category ---

        if category == "access_cards":
            tk.Label(sign_out_frame, text="Card Number:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.card_number_entry = tk.Entry(sign_out_frame)
            self.card_number_entry.grid(row=4, column=1, padx=5, pady=5)

        elif category == "Keys":
            tk.Label(sign_out_frame, text="Key Name:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.key_name_entry = tk.Entry(sign_out_frame)
            self.key_name_entry.grid(row=4, column=1, padx=5, pady=5)

        elif category == "Equipment":
            tk.Label(sign_out_frame, text="Item Type:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
            self.item_type_combobox = ttk.Combobox(sign_out_frame, values=["Laptop", "Projector", "Camera", "Other"])
            self.item_type_combobox.grid(row=4, column=1, padx=5, pady=5)

            tk.Label(sign_out_frame, text="Item Details:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
            self.item_details_entry = tk.Entry(sign_out_frame)
            self.item_details_entry.grid(row=5, column=1, padx=5, pady=5)

            tk.Button(sign_out_frame, text="Add", command=self.add_equipment_to_listbox).grid(row=6, column=1, padx=5, pady=5)

            # Equipment Listbox (with multiple selection)
            self.equipment_listbox = tk.Listbox(sign_out_frame, selectmode=tk.MULTIPLE)
            self.equipment_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Consistent Padding and Spacing within Subtab
        for i in range(10):  # Adjust based on the number of rows in your subtab
            sign_out_frame.rowconfigure(i, weight=1, pad=5)
        for i in range(2):  # Adjust based on the number of columns in your subtab
            sign_out_frame.columnconfigure(i, weight=1, pad=5)

        # --- Sign Out Button ---
        tk.Button(sign_out_frame, text="Sign Out", command=lambda: self.sign_out_item(category)).grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        return sign_out_frame

    def add_equipment_to_listbox(self):
        """Adds the selected item and details to the equipment listbox."""
        current_tab = self.tabs.tab(self.tabs.select(), "text")
        if current_tab in self.subtab_widgets:
            listbox = self.subtab_widgets[current_tab]["equipment_listbox"]

            item_type = self.item_type_combobox.get()
            item_details = self.item_details_entry.get()

            if item_type and item_details:
                display_text = f"{item_type} - {item_details}"
                listbox.insert(tk.END, display_text)
                self.item_details_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Missing Information", "Please select an item type and enter details.")

