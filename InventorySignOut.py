from app2 import db_handler
from gui_creation import SharedWidgets, AccessCardWidgets, KeyWidgets, EquipmentWidgets, GUICreation
import phonenumbers
import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

conn = sqlite3.connect("sign_outs.db")


class InventorySignOut:
	def __init__(self, root, db_handler, shared_widgets, gui_c6reator, access_card_widgets, key_widgets, equipment_widgets):
		"""Initializes the InventorySignOut application."""
		self.root = root
		self.root.title("Digital Sign Out")
		self.root = root
		self.db_handler = db_handler
		self.shared_widgets = shared_widgets
		self.gui_creator = gui_creator
		self.access_card_widgets = access_card_widgets
		self.key_widgets = key_widgets
		self.equipment_widgets = equipment_widgets

		# Tabs for signing out items
		self.tabs = ttk.Notebook(root)
		self.tabs.grid (pady=10, padx=10)
		# Dictionary to store signed out items
		db_handler.get_signed_out_items = {}

		# Dictionary to store subtab widgets
		self.subtab_widgets = {}

		# Create shared widgets
		self.shared_widgets = shared_widgets

		# Create category-specific widgets
				# Create tabs for each category
		for category in ["access_cards", "Keys", "Equipment"]:
			self.create_tab(gui_creator, category)
			self.update_signed_out_display(self.subtab_widgets[category]["at_a_glance_listbox"], category)
		# Select the first tab by default
		self.tabs.select(0)
		self.create_feedback_window()
		# Sign In Widget Stuff
		self.sign_in_listbox = None
##GUI Creation##
	def create_tab(self, category, gui_creator):
		"""Creates a tab for a specific item category."""
		tab = ttk.Frame(self.tabs)
		#self.tabs.add(tab, text=category.replace("s", ""))  # Remove plural 's'

		subtabs = ttk.Notebook(tab)
		subtabs.pack(pady=10, padx=10, fill="both", expand=True)

		# Initialize subtab-specific widgets for the category
		self.subtab_widgets[category] = {}

		self.create_sign_out_subtab(category, subtabs)
		self.create_at_a_glance_subtab(category, subtabs)
		self.create_sign_in_subtab(category, subtabs)
	###LEGCAY CODE###
	"""def create_sign_out_subtab(self, category, subtabs):
		#Creates the Sign Out subtab for a category.
		sign_out_frame = self.gui_creator.create_sign_out_subtab(category)
		subtabs.add(sign_out_frame, text="Sign Out")

		# Create widgets for each category
		self.subtab_widgets[category] = {}
		self.subtab_widgets[category].update(self.access_card_widgets.create_widgets(sign_out_frame) if category == "access_cards" else {})
		self.subtab_widgets[category].update(self.key_widgets.create_widgets(sign_out_frame) if category == "Keys" else {})
		self.subtab_widgets[category].update(self.equipment_widgets.create_widgets(sign_out_frame) if category == "Equipment" else {})
		# Create the feedback window
		self.create_feedback_window()
		# Create tabs for each category
		for category in ["accein gui_creation.py, how is shared widgets being drawn when accesscardwidgets (or others) ss_cards", "Keys", "Equipment"]:
			self.create_tab(category, gui_creator)
			self.update_signed_out_display(self.subtab_widgets[category]["at_a_glance_listbox"], category)
		# Select the first tab by default
		self.tabs.select(0)
		self.create_feedback_window()
		# Sign In Widget Stuff
		self.sign_in_listbox = None
		"""
	def create_sign_out_subtab(self, category, subtabs):
		"""Creates the "Sign Out" subtab for a category."""
		sign_out_frame = ttk.Frame(subtabs)
		subtabs.add(sign_out_frame, text="Sign Out")

		# Create widgets using gui_creation
		if category == "access_cards":
			self.card_number_entry = self.gui_creator.create_card_number_entry(sign_out_frame)
		elif category == "Keys":
			self.key_name_entry = self.gui_creator.create_key_name_entry(sign_out_frame)
		elif category == "Equipment":
			self.item_type_combobox = self.gui_creator.create_item_type_combobox(sign_out_frame)
			self.item_details_entry = self.gui_creator.create_item_details_entry(sign_out_frame)
			self.add_equipment_button = self.gui_creator.create_add_equipment_button(sign_out_frame, self.add_equipment_to_listbox)
			self.equipment_listbox = self.gui_creator.create_equipment_listbox(sign_out_frame)

		# Consistent Padding and Spacing within Subtab
		for i in range(10):  # Adjust based on the number of rows in your subtab
			sign_out_frame.rowconfigure(i, weight=1, pad=5)
		for i in range(2):  # Adjust based on the number of columns in your subtab
			sign_out_frame.columnconfigure(i, weight=1, pad=5)

		# --- Sign Out Button ---
		tk.Button(sign_out_frame, text="Sign Out", command=lambda: self.sign_out_item(category)).grid(row=8, column=0, columnspan=2, padx=5, pady=5)

		return sign_out_frame
	def update_signed_out_display(self, listbox, category="All"):
		"""Updates the listbox displaying signed-out items."""
		listbox.delete(0, tk.END)
		# Check if the database connection is open
		try:
			cursor = conn.cursor()
			cursor.execute("SELECT 1")
			print("Connection is alive")
			print(self.db_handler.get_signed_out_items)
			print(self.db_handler.get_signed_out_items.values())
			# Get items to display (all or filtered by category)
			#check if there are any signed out items
			items_to_display = self.db_handler.get_signed_out_items(category) if category != "All" else [
			item for cat_items in self.db_handler.get_signed_out_items.values() for item in cat_items
		]
			# Sort and display items
			for item in sorted(items_to_display, key=lambda x: x["hidden_timestamp"], reverse=True):
				formatted_timestamp = item["hidden_timestamp"].strftime("%Y-%m-%d %H:%M:%S")
				display_text = f"{item['user_name']} - {item['item_details']} - {formatted_timestamp}"
				listbox.insert(tk.END, display_text)

		except sqlite3.OperationalError as e:
			# Handle the case where the database file is not found or the table doesn't exist
			other_files = [f for f in os.listdir(".") if f.endswith(".db")]
			error_message = (
				"Database 'sign_outs.db' not found. Please make sure it exists in the current directory.\n"
				f"Other database files found: {other_files}"
			)
			print(error_message)  # Print to console
			print(f"Connection is not alive: {e}")
			messagebox.showerror("Database Error", error_message)  # Show error in GUI
		finally:
			# Close the database connection
			if conn:
				conn.close()

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
	def sign_out_item(self, category, db_handler):
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
			db_handler.add_item(category, user_name, category, item_details, phonenumbers.national_number)
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
		if sign_in(itusername, pin):  # Replace with your actual authentication logic
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

if __name__ == "__main__":		# Create the main window
	root = tk.Tk()
	root.title("Digital Sign Out")

	# Create instances of the required classes
	db_handler = db_handler()
	shared_widgets = SharedWidgets(root)
	gui_creator = GUICreation(root)
	access_card_widgets = AccessCardWidgets(root)
	key_widgets = KeyWidgets(root)
	equipment_widgets = EquipmentWidgets(root)


	# Create an instance of the InventorySignOut class
	app = InventorySignOut(root, db_handler, shared_widgets, gui_creator, access_card_widgets, key_widgets, equipment_widgets)

	# Start the main event loop
	root.mainloop()