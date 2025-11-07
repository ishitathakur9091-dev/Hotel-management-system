import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# --- Database Connection ---
def connect_db():
    try:
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            status TEXT DEFAULT 'Available'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            room_id INTEGER,
            check_in TEXT,
            check_out TEXT,
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
            FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
        )
        """)

        conn.commit()
        return conn
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None


# --- Add Customer ---
def add_customer():
    name = entry_name.get()
    phone = entry_phone.get()
    email = entry_email.get()
    address = entry_address.get()

    if name == "" or phone == "" or email == "" or address == "":
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customers (full_name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully!")
        clear_customer_fields()


# --- Add Booking ---
def add_booking():
    cust_id = entry_cust_id.get()
    room_id = entry_room_id.get()
    check_in = entry_checkin.get()
    check_out = entry_checkout.get()

    if cust_id == "" or room_id == "" or check_in == "" or check_out == "":
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Rooms WHERE room_id = ?", (room_id,))
        room = cursor.fetchone()

        if not room:
            cursor.execute("INSERT INTO Rooms (room_id, room_number, status) VALUES (?, ?, 'Available')", 
                           (room_id, f"Room {room_id}"))

        cursor.execute(
            "INSERT INTO Bookings (customer_id, room_id, check_in, check_out) VALUES (?, ?, ?, ?)",
            (cust_id, room_id, check_in, check_out)
        )

        cursor.execute("UPDATE Rooms SET status = 'Booked' WHERE room_id = ?", (room_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Booking added successfully!")
        clear_booking_fields()


# --- Clear Fields ---
def clear_customer_fields():
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_address.delete(0, tk.END)

def clear_booking_fields():
    entry_cust_id.delete(0, tk.END)
    entry_room_id.delete(0, tk.END)
    entry_checkin.delete(0, tk.END)
    entry_checkout.delete(0, tk.END)


# --- View Customers ---
def view_customers():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customers")
        rows = cursor.fetchall()
        conn.close()

        win = tk.Toplevel(root)
        win.title("All Customers")
        win.geometry("700x400")

        tree = ttk.Treeview(win, columns=("ID", "Name", "Phone", "Email", "Address"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Full Name")
        tree.heading("Phone", text="Phone")
        tree.heading("Email", text="Email")
        tree.heading("Address", text="Address")
        tree.pack(fill="both", expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)


# --- View Bookings ---
def view_bookings():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT B.booking_id, C.full_name, R.room_number, B.check_in, B.check_out
            FROM Bookings B
            JOIN Customers C ON B.customer_id = C.customer_id
            JOIN Rooms R ON B.room_id = R.room_id
        """)
        rows = cursor.fetchall()
        conn.close()

        win = tk.Toplevel(root)
        win.title("All Bookings")
        win.geometry("700x400")

        tree = ttk.Treeview(win, columns=("Booking ID", "Customer Name", "Room", "Check-in", "Check-out"), show="headings")
        tree.heading("Booking ID", text="Booking ID")
        tree.heading("Customer Name", text="Customer Name")
        tree.heading("Room", text="Room")
        tree.heading("Check-in", text="Check-in Date")
        tree.heading("Check-out", text="Check-out Date")
        tree.pack(fill="both", expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)


# --- GUI Setup ---
root = tk.Tk()
root.title("🏨 Hotel Management System (SQLite3)")
root.geometry("500x700")
root.config(bg="#f0f8ff")

tk.Label(root, text="Add Customer Details", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=10)
tk.Label(root, text="Full Name:", bg="#f0f8ff").pack()
entry_name = tk.Entry(root, width=40)
entry_name.pack()

tk.Label(root, text="Phone:", bg="#f0f8ff").pack()
entry_phone = tk.Entry(root, width=40)
entry_phone.pack()

tk.Label(root, text="Email:", bg="#f0f8ff").pack()
entry_email = tk.Entry(root, width=40)
entry_email.pack()

tk.Label(root, text="Address:", bg="#f0f8ff").pack()
entry_address = tk.Entry(root, width=40)
entry_address.pack()

tk.Button(root, text="Add Customer", command=add_customer, bg="#4caf50", fg="white", width=20).pack(pady=10)
tk.Button(root, text="View Customers", command=view_customers, bg="#8e44ad", fg="white", width=20).pack(pady=5)

tk.Label(root, text="Add Booking Details", font=("Arial", 16, "bold"), bg="#f0f8ff").pack(pady=15)

tk.Label(root, text="Customer ID:", bg="#f0f8ff").pack()
entry_cust_id = tk.Entry(root, width=40)
entry_cust_id.pack()

tk.Label(root, text="Room ID:", bg="#f0f8ff").pack()
entry_room_id = tk.Entry(root, width=40)
entry_room_id.pack()

tk.Label(root, text="Check-in Date (YYYY-MM-DD):", bg="#f0f8ff").pack()
entry_checkin = tk.Entry(root, width=40)
entry_checkin.pack()

tk.Label(root, text="Check-out Date (YYYY-MM-DD):", bg="#f0f8ff").pack()
entry_checkout = tk.Entry(root, width=40)
entry_checkout.pack()

tk.Button(root, text="Add Booking", command=add_booking, bg="#2196f3", fg="white", width=20).pack(pady=10)
tk.Button(root, text="View Bookings", command=view_bookings, bg="#ff9800", fg="white", width=20).pack(pady=5)

root.mainloop()
