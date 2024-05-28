import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import sqlite3
import re
import os
import phonenumbers

## BACKEND ##

class db_handler:
	def __init__(self):
		self.conn = sqlite3.connect("sign_outs.db")
		self.cursor = self.conn.cursor()
		if not os.path.exists("sign_outs.db"):
			self.create_database()
			print("Database created successfully.")
		else:
			print("Database already exists continuing.")
		self.conn.commit()
		self.conn.close()
	
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
	#check before creating the DB TODO 
	#create_database()
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
		print("connection closing")
		conn.close()
		return data

	def sign_in(username, pin):
		"""Placeholder for authentication logic. Replace with your implementation."""
		# Compare username and pin with stored credentials
		return username == "admin" and pin == "1234"  # Example: Hardcoded credentials (insecure!)
				
				
	def add_item(self, category, user_name, item_type, item_details, comments):
		"""Adds a new item to the sign-out log in the SQLite database."""
		signed_out_items = self.get_signed_out_items(category)  # Get the list of signed-out items
		timestamp = datetime.datetime.now().isoformat()
		new_item = {
			"timestamp": timestamp,
			"hidden_timestamp": datetime.datetime.now(),
			"user_name": user_name,
			"item_type": item_type,
			"item_details": item_details,
			"comments": comments
		}
		self.save_data
		