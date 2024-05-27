import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sqlite3
import re
import os
import phonenumbers


## BACKEND ##

def create_database():
	"""Creates the SQLite database and tables if they don't exist."""
	conn = sqlite3.connect("sign_outs.db")
	cursor = conn.cursor()

	# Create tables for each category
	for category in ["access_cards", "Keys", "Equipment"]:
		cursor.execute(f"""
			CREATE TABLE IF NOT EXISTS {category} (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp TEXT,
				hidden_timestamp TIMESTAMP,
				user_name TEXT,
				item_type TEXT,
				item_details TEXT,
				name TEXT,
				comments TEXT
			)
		""")
	conn.commit()
	conn.close()

"""
id: A unique identifier for each sign-out entry (auto-incrementing).
timestamp: The date and time of the sign-out (text format for flexibility).
hidden_timestamp: A timestamp for internal sorting (SQLite's TIMESTAMP type).
user_name: The name of the person signing out the item.
item_type: The category of the item (Access Card, Key, Equipment).
item_details: Specific details about the item (e.g., card number, key name).
name: redundant field, can be removed
comments: Additional comments about the sign-out.
"""
create_database()
def load_data(category, month=None):
	"""Loads sign-out data from the SQLite database for the given category and month."""
	if month is None:
		month = datetime.datetime.now().strftime("%B")  # Get current month if not provided

	try:
		conn = sqlite3.connect("sign_outs.db")
		cursor = conn.cursor()
		query = f"SELECT * FROM {category} WHERE strftime('%-m', timestamp) = ?"
		cursor.execute(query, (month,))
		rows = cursor.fetchall()
		# Convert rows to a list of dictionaries
		data = []
		for row in rows:
			data.append({
				"id": row[0],
				"timestamp": row[1],
				"hidden_timestamp": row[2],
				"user_name": row[3],
				"item_type": row[4],
				"item_details": row[5],
				"comments": row[6]
			})

	except sqlite3.OperationalError:
		# Handle the case where the database file is not found or the table doesn't exist
		other_files = [f for f in os.listdir(".") if f.endswith(".db")]
		error_message = (
			"Database 'sign_outs.db' not found. Please make sure it exists in the current directory.\n"
			f"Other database files found: {other_files}"
		)
		print(error_message)  # Print to console
		messagebox.showerror("Database Error", error_message)  # Show error in GUI
		return []

	finally:
		conn.close()

	return data

def save_data(category, new_item):
	"""Saves a new sign-out entry to the SQLite database."""
	conn = sqlite3.connect("sign_outs.db")
	cursor = conn.cursor()

	try:
		# Sanitize input to prevent SQL injection
		for key, value in new_item.items():
			if isinstance(value, str):
				new_item[key] = value.replace("'", "''")  # Escape single quotes

		cursor.execute(f"""
			INSERT INTO {category} (timestamp, hidden_timestamp, user_name, item_type, item_details, comments)
			VALUES (?, ?, ?, ?, ?, ?)
		""", (
			new_item["timestamp"],
			new_item["hidden_timestamp"],
			new_item["user_name"],
			new_item["item_type"],
			new_item["item_details"],
			new_item["comments"]
		))

		conn.commit()
	except sqlite3.Error as e:
		# Handle potential database errors (e.g., unique constraint violations)
		messagebox.showerror("Database Error", f"Error saving data: {e}")
	finally:
		conn.close()
		
def get_signed_out_items(category):
	"""Gets the list of currently signed-out items for a category."""
	conn = sqlite3.connect("sign_outs.db")
	cursor = conn.cursor()
	cursor.execute(f"SELECT * FROM {category}")
	rows = cursor.fetchall()

	# Convert rows to a list of dictionaries
	data = []
	for row in rows:
		data.append({
			"id": row[0],
			"timestamp": row[1],
			"hidden_timestamp": row[2],
			"user_name": row[3],
			"item_type": row[4],
			"item_details": row[5],
			"comments": row[6]
		})

	conn.close()
	return data

def sign_in(username, pin):
	"""Placeholder for authentication logic. Replace with your implementation."""
	# Compare username and pin with stored credentials
	return username == "admin" and pin == "1234"  # Example: Hardcoded credentials (insecure!)
			
			
def add_item(category, user_name, item_type, item_details, comments):
	"""Adds a new item to the sign-out log in the SQLite database."""
	timestamp = datetime.datetime.now().isoformat()
	new_item = {
		"timestamp": timestamp,
		"hidden_timestamp": datetime.datetime.now(),
		"user_name": user_name,
		"item_type": item_type,
		"item_details": item_details,
		"comments": comments
	}
	save_data(category, new_item)  # Save to database
	signed_out_items.setdefault(category, []).append(new_item)  # Update dictionary


## FRONT END ##
class InventorySignOut:
	def __init__(self, root):
		"""Initializes the InventorySignOut application."""
		self.root = root
		self.root.title("Digital Sign Out")

		# Tabs for signing out items
		self.tabs = ttk.Notebook(root)
		self.tabs.pack(pady=10, padx=10, fill="both", expand=True)

		# Dictionary to store signed out items
		self.signed_out_items = {}

		# Dictionary to store subtab widgets
		self.subtab_widgets = {}

		# Create tabs for each category
		for category in ["access_cards", "Keys", "Equipment"]:
			self.create_tab(category)
			self.update_signed_out_display(self.subtab_widgets[category]["at_a_glance_listbox"], category)
		# Select the first tab by default
		self.tabs.select(0)
		self.create_feedback_window()
		# Sign In Widget Stuff
		self.sign_in_listbox = None
			
	def create_shared_widgets(self, sign_out_frame):
		"""Creates shared widgets for name, date, and phone number."""
		# --- Widgets for Name, Date, Phone Number --- 
		
		tk.Label(sign_out_frame, text="Name (First Last):").grid(row=0, column=0, sticky="e")
		self.user_name_entry = tk.Entry(sign_out_frame)
		self.user_name_entry.grid(row=0, column=1, sticky="w")

		tk.Label(sign_out_frame, text="Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
		self.date_label = tk.Label(sign_out_frame, text=datetime.date.today())
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
		tk.Label(sign_out_frame, text="Phone Number (XXX-XXX-XXXX):").grid(row=2, column=0, sticky="e")
		self.phone_number_entry = tk.Entry(sign_out_frame)
		self.phone_number_entry.grid(row=2, column=1, sticky="w")
		self.phone_number_entry.bind("<KeyRelease>", format_phone_number)  # Use self.phone_number_entry


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
###############GUI CREATION #############################
	def create_tab(self, category):
		"""Creates a tab for a specific item category."""
		tab = ttk.Frame(self.tabs)
		self.tabs.add(tab, text=category.replace("s", ""))  # Remove plural 's'

		subtabs = ttk.Notebook(tab)
		subtabs.pack(pady=10, padx=10, fill="both", expand=True)

		# Initialize subtab-specific widgets for the category
		self.subtab_widgets[category] = {}

		self.create_sign_out_subtab(category, subtabs)
		self.create_at_a_glance_subtab(category, subtabs)
		self.create_sign_in_subtab(category, subtabs)

	def create_sign_out_subtab(self, category, subtabs):
		"""Creates the "Sign Out" subtab for a category."""
		sign_out_frame = ttk.Frame(subtabs)
		subtabs.add(sign_out_frame, text="Sign Out")
		self.create_shared_widgets(sign_out_frame)

		# --- Dynamically create fields based on category ---

		if category == "access_cards":
			tk.Label(sign_out_frame, text="Card Number:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
			self.card_number_entry = tk.Entry(sign_out_frame)
			self.card_number_entry.grid(row=4, column=1, padx=5, pady=5)
			self.subtab_widgets[category]["card_number_entry"] = self.card_number_entry

		elif category == "Keys":
			tk.Label(sign_out_frame, text="Key Name:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
			self.key_name_entry = tk.Entry(sign_out_frame)
			self.key_name_entry.grid(row=4, column=1, padx=5, pady=5)
			self.subtab_widgets[category]["key_name_entry"] = self.key_name_entry

		elif category == "Equipment":
			tk.Label(sign_out_frame, text="Item Type:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
			self.item_type_combobox = ttk.Combobox(sign_out_frame, values=["Laptop", "Projector", "Camera", "Other"])
			self.item_type_combobox.grid(row=4, column=1, padx=5, pady=5)

			tk.Label(sign_out_frame, text="Item Details:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
			self.item_details_entry = tk.Entry(sign_out_frame)
			self.item_details_entry.grid(row=5, column=1, padx=5, pady=5)

			tk.Button(sign_out_frame, text="Add", command=self.add_equipment_to_listbox).grid(row=6, column=1, padx=5, pady=5)
			self.subtab_widgets[category]["item_type_combobox"] = self.item_type_combobox
			self.subtab_widgets[category]["item_details_entry"] = self.item_details_entry

			# Equipment Listbox (with multiple selection)
			self.equipment_listbox = tk.Listbox(sign_out_frame, selectmode=tk.MULTIPLE)
			self.equipment_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
			self.subtab_widgets[category]["equipment_listbox"] = self.equipment_listbox

		# Consistent Padding and Spacing within Subtab
		for i in range(10):  # Adjust based on the number of rows in your subtab
			sign_out_frame.rowconfigure(i, weight=1, pad=5)
		for i in range(2):  # Adjust based on the number of columns in your subtab
			sign_out_frame.columnconfigure(i, weight=1, pad=5)
			
			
		# --- Sign Out Button ---
		tk.Button(sign_out_frame, text="Sign Out", command=lambda: self.sign_out_item(category)).grid(row=8, column=0, columnspan=2, padx=5, pady=5)

	def update_signed_out_display(self, listbox, category="All"):
		"""Updates the listbox displaying signed-out items."""
		listbox.delete(0, tk.END)
		# Get items to display (all or filtered by category)
		items_to_display = get_signed_out_items(category) if category != "All" else [
			item for cat_items in signed_out_items.values() for item in cat_items
		]
		# Sort and display items
		for item in sorted(items_to_display, key=lambda x: x["hidden_timestamp"], reverse=True):
			formatted_timestamp = item["hidden_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
			display_text = f"{item['user_name']} - {item['item_details']} - {formatted_timestamp}"
			listbox.insert(tk.END, display_text)

	def create_at_a_glance_subtab(self, category, subtabs):
		"""Creates the "At a Glance" subtab."""
		at_a_glance_frame = ttk.Frame(subtabs)
		subtabs.add(at_a_glance_frame, text="At a Glance")

		tk.Label(at_a_glance_frame, text="Currently Signed Out:").grid(row=0, column=0, pady=(10, 5), sticky="w")
		listbox = tk.Listbox(at_a_glance_frame)
		listbox.grid(row=1, column=0, sticky="nsew")
		self.update_signed_out_display(listbox, category)

		# Store reference to the listbox for later updates
		self.subtab_widgets[category]["at_a_glance_listbox"] = listbox

	def create_sign_in_subtab(self, category, subtabs):
		"""Creates the "Sign In" subtab."""
		sign_in_frame = ttk.Frame(subtabs)
		subtabs.add(sign_in_frame, text="Sign In")
		
		tk.Label(sign_in_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
		self.itusername_entry = tk.Entry(sign_in_frame)
		self.itusername_entry.grid(row=0, column=1, padx=5, pady=5)

		tk.Label(sign_in_frame, text="PIN:").grid(row=1, column=0, padx=5, pady=5)
		self.pin_entry = tk.Entry(sign_in_frame, show="*")
		self.pin_entry.grid(row=1, column=1, padx=5, pady=5)
		# Item Selection Listbox
		self.sign_in_listbox = tk.Listbox(sign_in_frame)
		self.sign_in_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

		# Update the Listbox with signed out items
		self.update_signed_out_display(self.sign_in_listbox, category)

		tk.Button(sign_in_frame, text="Sign In", command=lambda: self.sign_in_item(category)).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

###############INTERFACE FUNC###############################################
	def sign_out_item(self, category):
		"""Handles the sign-out process for an item."""
		user_name = self.user_name_entry.get()
		phone_number_str = self.phone_number_entry.get()

		if not self.validate_input(self.user_name_entry, phone_number_str, category):
			return  # If validation fails, exit the function

		# Get Item Details (Simplified)
		item_details_entry = self.subtab_widgets[category].get(f"{category.replace('s', '')}_number_entry", None)
		if item_details_entry:
			item_details = item_details_entry.get()
		elif category == "Equipment":
			selected_items = self.equipment_listbox.curselection()
			if not selected_items:
				# No need for a warning here, as validate_input already handled it
				return 
			item_details = "\n".join([self.equipment_listbox.get(i) for i in selected_items])
			# Clear selected items
			for i in reversed(selected_items):
				self.equipment_listbox.delete(i)
		# Data Logging and GUI Updates
		try:
			# Pass the correctly parsed phone number (national_number)
			add_item(category, user_name, category, item_details, phone_number.national_number)
			# Clear input fields
			self.user_name_entry.delete(0, tk.END)
			self.phone_number_entry.delete(0, tk.END)
			if item_details_entry:
				item_details_entry.delete(0, tk.END)
			# Success message
			messagebox.showinfo("Signed Out", f"{category[:-1]} signed out successfully!")
			# Update the "At a Glance" display
			for cat in self.subtab_widgets:  # Update all "At a Glance" tabs
				self.update_signed_out_display(self.subtab_widgets[cat]["at_a_glance_listbox"], cat)
			# Update sign in listbox
			self.update_signed_out_display(self.sign_in_listbox, category)
		except Exception as e:
			messagebox.showerror("Error", f"An error occurred while signing out: {e}")

		
	def validate_input(self, user_name, phone_number_str, category):
		"""Validates user input for signing out items."""
		# Check if name is entered
		user_name = self.user_name_entry.get()
		if len(user_name.strip()) == 0:
			messagebox.showwarning("Missing Name", "Please enter your name.")
			return False

		# Check if phone number is entered (simplified)
		if not phone_number_str:
			messagebox.showwarning("Missing Phone Number", "Please enter your phone number.")
			return False

		# Additional checks based on category
		if category == "Equipment":
			selected_items = self.equipment_listbox.curselection()
			if not selected_items:
				messagebox.showwarning("No Item Selected", "Please select at least one equipment item to sign out.")
				return False
		elif category in ["access_cards", "Keys"]:
			# Get appropriate entry widget for the category
			item_details_entry = self.subtab_widgets[category].get(f"{category.replace('s', '')}_number_entry")
			if not item_details_entry or not item_details_entry.get():
				messagebox.showwarning("Missing Details", f"Please enter {category[:-1]} number/name.")
				return False

		return True  # All validations passed


	def sign_in_item(self, category):
		"""Handles the sign-in process."""
		itusername = self.iteusername_entry.get()
		pin = self.pin_entry.get()
#######PLACEHOLDER ##############################################################
		if sign_in(username, pin):  # Replace with your actual authentication logic
			if self.sign_in_listbox is not None:  # Check if the listbox exists
				selected_index = self.sign_in_listbox.curselection()
			else:
				messagebox.showerror("Error", "Sign-in listbox not initialized.")
		else:
			messagebox.showerror("Error", "Invalid username or PIN.")
#################################################################################
	def remove_signed_out_item(self, category, item_details):
		"""Removes a signed-out item from the database."""
		conn = sqlite3.connect("sign_outs.db")
		cursor = conn.cursor()
		cursor.execute(f"DELETE FROM {category} WHERE item_details = ?", (item_details,))
		conn.commit()
		conn.close()
		self.update_signed_out_display(self.subtab_widgets[category]["at_a_glance_listbox"], category) 


	def show_feedback(self, message, error_code=None):
		"""Displays feedback to the user."""
		# ...

	def create_feedback_window(self):
		"""Creates a separate window for feedback messages."""
		# ...


if __name__ == "__main__":
	root = tk.Tk()
	app = InventorySignOut(root)
	root.mainloop()
