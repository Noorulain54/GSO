#correct  program  date 3/16/2025
# 1–3: Importing Libraries
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox

# Connect to MySQL #  5–13: Connecting to MySQL
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="winner12",
        database="gso_management1"
    )
    if connection.is_connected():
        print("Connected to the database.")
except Error as e:
    print("Error connecting to MySQL:", e)
    exit()
# Table fields dictionary
# 15–23: Defining Table Fields  #  Insert Data Function
table_fields = {
    "student_data": ["rq_no","registration_number", "cnic", "name", "father_name", "gender", "DOB","registration_date", "Program", "department",  "session", "district", "contact_number"],
    "student_research": ["rq_no","synopsis_title","supervisor_id","meeting_id","co_supervisor_id" ],
    "meeting": ["meeting_id", "meeting_number", "date"],
    "degree_awarded": [ "rq_no", "meeting_id"],
    "admission_canceled": [ "rq_no","meeting_id"],
    "supervisor_data": ["supervisor_id", "designation", "department","cnic", "name", "dob", "contact_number", "qualification","status"],
    "progress": ["RQ_no", "1st_progress_rep", "2nd_progress_rep", "3rd_progress_rep", "4th_progress_rep", "5th_progress_rep"]
}

# Insert data into a specific table
def insert_data(table_name, entries):
    fields = table_fields[table_name]
    data = [entry.get() for entry in entries.values()]
    query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})"

    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        messagebox.showinfo("Success", "Data Saved Successfully.")
        for entry in entries.values():
            entry.delete(0, tk.END)
    except Error as e:
        messagebox.showerror("Error", f"Failed to insert data: {e}")
    finally:
        cursor.close()

# Display data for a table 50–85: Display Table Data + Delete Feature
def display_data(table_name):
    for widget in root.winfo_children():
        widget.destroy()  # Clear the window before showing new content

    tk.Label(root, text=f"{table_name} Data", font=("Arial", 16)).pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    fields = table_fields[table_name]
    tree = ttk.Treeview(frame, columns=fields, show="headings", height=10)
    for field in fields:
        tree.heading(field, text=field)
        tree.column(field, anchor="center")
    tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
    except Error as e:
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
    finally:
        cursor.close()

    def delete_data():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected to delete.")
            return

        selected_data = tree.item(selected_item)["values"]
        primary_key = fields[0]
        primary_key_value = selected_data[0]

        query = f"DELETE FROM {table_name} WHERE {primary_key} = %s"
        cursor = connection.cursor()
        try:
            cursor.execute(query, (primary_key_value,))
            connection.commit()
            messagebox.showinfo("Success", "Data Deleted Successfully.")
            tree.delete(selected_item)
        except Error as e:
            messagebox.showerror("Error", f"Failed to delete data: {e}")
        finally:
            cursor.close()

    def edit_data():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "No item selected to edit.")
            return

        selected_data = tree.item(selected_item)["values"]
        edit_window = tk.Toplevel(root)
        edit_window.title(f"Edit {table_name} Record")
        
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(edit_window, text=field).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(edit_window, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, selected_data[i])
            entries[field] = entry

        def update_data():
            primary_key = fields[0]
            primary_key_value = selected_data[0]
            
            set_clause = ", ".join([f"{field} = %s" for field in fields])
            data = [entry.get() for entry in entries.values()]
            
            query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
            data.append(primary_key_value)
            
            cursor = connection.cursor()
            try:
                cursor.execute(query, data)
                connection.commit()
                messagebox.showinfo("Success", "Data Updated Successfully.")
                edit_window.destroy()
                display_data(table_name)  # Refresh the display
            except Error as e:
                messagebox.showerror("Error", f"Failed to update data: {e}")
            finally:
                cursor.close()

        tk.Button(edit_window, text="Update", command=update_data).grid(row=len(fields), column=0, columnspan=2, pady=10)

    tk.Button(root, text="Delete Selected", command=delete_data).pack(pady=5)
    tk.Button(root, text="Edit Selected", command=edit_data).pack(pady=5)
    tk.Button(root, text="Back to Home", command=show_home).pack(pady=10)

# Search by RQ number 87–122: Search by RQ Number
def search_by_rq(table_name):
    for widget in root.winfo_children():
        widget.destroy()  # Clear previous content

    tk.Label(root, text=f"Search {table_name} by RQ", font=("Arial", 16)).pack(pady=10)
    
    tk.Label(root, text="Enter RQ Number:").pack(pady=10)
    rq_entry = tk.Entry(root)
    rq_entry.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack(pady=10)

    result_tree = ttk.Treeview(frame, columns=table_fields[table_name], show="headings")
    for field in table_fields[table_name]:
        result_tree.heading(field, text=field)
        result_tree.column(field, anchor="center")
    result_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def perform_search():
        rq_no = rq_entry.get()
        query = f"SELECT * FROM {table_name} WHERE rq_no = %s"
        cursor = connection.cursor()
        try:
            cursor.execute(query, (rq_no,))
            rows = cursor.fetchall()
            result_tree.delete(*result_tree.get_children())
            for row in rows:
                result_tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Error", f"Failed to search data: {e}")
        finally:
            cursor.close()

    tk.Button(root, text="Search", command=perform_search).pack(pady=10)
    tk.Button(root, text="Back to Home", command=show_home).pack(pady=10)

# Open table management interface inside the same window #Form to Insert, Display, Search Data
def open_table(table_name):
    for widget in root.winfo_children():
        widget.destroy()  # Clear previous content

    tk.Label(root, text=f"{table_name} Management", font=("Arial", 16)).pack(pady=10)
    
    frame = tk.Frame(root)
    frame.pack(pady=10)

    fields = table_fields[table_name]
    entries = {}

    for i, field in enumerate(fields):
        tk.Label(frame, text=field, width=15, anchor="w").grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(frame, width=30)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[field] = entry

    tk.Button(root, text="Insert Data", command=lambda: insert_data(table_name, entries)).pack(pady=5)
    tk.Button(root, text="Display Data", command=lambda: display_data(table_name)).pack(pady=5)
    tk.Button(root, text="Search by RQ", command=lambda: search_by_rq(table_name)).pack(pady=5)
    tk.Button(root, text="Back to Home", command=show_home).pack(pady=10)

# Show home page # 
def show_home():
    for widget in root.winfo_children():
        widget.destroy()  # Clear previous content

    tk.Label(root, text="GSO Management System", font=("Arial", 16)).pack(pady=20)
    
    tk.Label(root, text="Select a Table to Manage:", font=("Arial", 14)).pack(pady=10)
    
    for table in table_fields.keys():
        tk.Button(root, text=table, font=("Arial", 12), width=30, command=lambda t=table: open_table(t)).pack(pady=5)

# Main Tkinter interface
root = tk.Tk()
root.title("GSO Management System")
root.geometry("600x600")
show_home()  # Show home page on startup

# Handle application exit
def on_closing():
    if connection.is_connected():
        connection.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()