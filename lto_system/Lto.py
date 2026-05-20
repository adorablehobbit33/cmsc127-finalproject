import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from db import fetch_all, execute_query
import datetime

class BaseManagementWindow:
    def __init__(self, parent, title, columns, col_widths, table_name, primary_key):
        self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.geometry("1200x950")
        
        self.columns = columns
        self.col_widths = col_widths
        self.table_name = table_name
        self.primary_key = primary_key
        
        self.editing_id = tk.StringVar(value="")
        
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        tk.Label(self.win, text=self.win.title(), font=("Arial", 16, "bold")).pack(pady=10)

        # Search Frame
        self.search_frame = tk.LabelFrame(self.win, text=f"Search {self.table_name.replace('_', ' ').capitalize()}", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.search_frame.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(self.search_frame, text="Search:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_entry = tk.Entry(self.search_frame, width=40, font=("Arial", 11))
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(self.search_frame, text="SEARCH", command=self.search, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5).grid(row=0, column=2, padx=20)
        tk.Button(self.search_frame, text="REFRESH / SHOW ALL", command=self.refresh_table, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5).grid(row=0, column=3, padx=10)

        # Treeview
        self.tree = ttk.Treeview(self.win, columns=self.columns, show="headings", height=10)
        for col, width in zip(self.columns, self.col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        self.tree.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # Form Frame
        self.form_frame = tk.LabelFrame(self.win, text="Details & Actions", font=("Arial", 12, "bold"), padx=10, pady=8)
        self.form_frame.pack(pady=5, fill=tk.X, padx=10)

        self.mode_label = tk.Label(self.form_frame, text="✚  ADD MODE  –  fill in the fields below", font=("Arial", 10, "italic"), fg="#4CAF50")
        self.mode_label.grid(row=0, column=0, columnspan=4, pady=(0, 6), sticky="w")

        self.setup_form_fields()

        # Buttons
        btn_row = tk.Frame(self.form_frame)
        btn_row.grid(row=100, column=0, columnspan=4, pady=10)

        self.add_btn = tk.Button(btn_row, text="➕  ADD", command=self.add_record, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=18, pady=5)
        self.add_btn.grid(row=0, column=0, padx=8)

        self.update_btn = tk.Button(btn_row, text="✏  UPDATE", command=self.update_record, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=18, pady=5, state="disabled")
        self.update_btn.grid(row=0, column=1, padx=8)

        tk.Button(btn_row, text="🗑  DELETE SELECTED", command=self.delete_record, bg="#f44336", fg="white", font=("Arial", 10, "bold"), padx=18, pady=5).grid(row=0, column=2, padx=8)
        tk.Button(btn_row, text="✖  CLEAR / NEW", command=self.clear_form, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), padx=18, pady=5).grid(row=0, column=3, padx=8)

        tk.Button(self.win, text="CLOSE", command=self.win.destroy, bg="#555555", fg="white", font=("Arial", 11, "bold"), padx=30, pady=5).pack(pady=10)

    def setup_form_fields(self):
        pass

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = self.get_fetch_all_query()
        rows = fetch_all(query)
        for row in rows:
            self.tree.insert("", tk.END, values=self.format_row_data(row))

    def search(self):
        term = self.search_entry.get().strip()
        if not term:
            self.refresh_table()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        query, params = self.get_search_query(term)
        rows = fetch_all(query, params)
        for row in rows:
            self.tree.insert("", tk.END, values=self.format_row_data(row))

    def on_row_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            values = self.tree.item(sel[0], "values")
            self.populate_form(values)

    def set_add_mode(self):
        self.editing_id.set("")
        self.mode_label.config(text="✚  ADD MODE  –  fill in the fields below", fg="#4CAF50")
        self.add_btn.config(state="normal")
        self.update_btn.config(state="disabled")
        self.enable_pk_field()

    def set_edit_mode(self, record_id):
        self.editing_id.set(record_id)
        self.mode_label.config(text=f"✏  EDIT MODE  –  editing  {record_id}  ({self.primary_key.replace('_', ' ')} locked)", fg="#FF9800")
        self.add_btn.config(state="disabled")
        self.update_btn.config(state="normal")
        self.disable_pk_field()

    def clear_form(self):
        self.set_add_mode()

    def populate_form(self, values):
        pass

    def get_fetch_all_query(self):
        return f"SELECT * FROM {self.table_name} LIMIT 100"

    def get_search_query(self, term):
        return f"SELECT * FROM {self.table_name} WHERE {self.primary_key} LIKE %s", (f"%{term}%",)

    def format_row_data(self, row):
        return tuple(row.values())

    def add_record(self):
        pass

    def update_record(self):
        pass

    def delete_record(self):
        sel = self.tree.selection()
        if sel:
            record_id = self.tree.item(sel[0], "values")[0]
        else:
            record_id = self.get_pk_value()
        if not record_id:
            messagebox.showwarning("Warning", "Select a row or enter ID first")
            return
        if messagebox.askyesno("Confirm", f"Delete record '{record_id}'?"):
            ok, err = execute_query(f"DELETE FROM {self.table_name} WHERE {self.primary_key} = %s", (record_id,))
            if ok:
                messagebox.showinfo("Success", "Deleted!"); self.clear_form(); self.refresh_table()
            else:
                messagebox.showerror("Error", f"Failed: {err}")

    def get_pk_value(self):
        return ""

    def enable_pk_field(self):
        pass

    def disable_pk_field(self):
        pass

class DriverManagement(BaseManagementWindow):
    def __init__(self, parent):
        columns = ("License No", "Full Name", "Type", "Status", "Sex", "DOB", "Address")
        widths = [120, 200, 150, 100, 70, 100, 300]
        super().__init__(parent, "Driver Management", columns, widths, "driver", "license_number")

    def setup_form_fields(self):
        LEFT = dict(padx=8, pady=4, sticky="e")
        ENTRY_W = 28
        tk.Label(self.form_frame, text="License Number:", font=("Arial", 10)).grid(row=1, column=0, **LEFT)
        self.lic_entry = tk.Entry(self.form_frame, width=ENTRY_W, font=("Arial", 10))
        self.lic_entry.grid(row=1, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="First Name:", font=("Arial", 10)).grid(row=2, column=0, **LEFT)
        self.first_entry = tk.Entry(self.form_frame, width=ENTRY_W, font=("Arial", 10))
        self.first_entry.grid(row=2, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="Middle Name:", font=("Arial", 10)).grid(row=3, column=0, **LEFT)
        self.mid_entry = tk.Entry(self.form_frame, width=ENTRY_W, font=("Arial", 10))
        self.mid_entry.grid(row=3, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="Last Name:", font=("Arial", 10)).grid(row=4, column=0, **LEFT)
        self.last_entry = tk.Entry(self.form_frame, width=ENTRY_W, font=("Arial", 10))
        self.last_entry.grid(row=4, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="Date of Birth:", font=("Arial", 10)).grid(row=5, column=0, **LEFT)
        self.dob_entry = DateEntry(self.form_frame, width=ENTRY_W - 2, font=("Arial", 10), date_pattern="yyyy-mm-dd")
        self.dob_entry.grid(row=5, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="Sex:", font=("Arial", 10)).grid(row=6, column=0, **LEFT)
        self.sex_var = tk.StringVar(value="Male")
        ttk.Combobox(self.form_frame, textvariable=self.sex_var, values=["Male", "Female"], width=ENTRY_W - 2, state="readonly").grid(row=6, column=1, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="License Type:", font=("Arial", 10)).grid(row=1, column=2, **LEFT)
        self.type_var = tk.StringVar(value="Non-Professional")
        ttk.Combobox(self.form_frame, textvariable=self.type_var, values=["Student Permit", "Non-Professional", "Professional"], width=ENTRY_W, state="readonly").grid(row=1, column=3, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="License Status:", font=("Arial", 10)).grid(row=2, column=2, **LEFT)
        self.status_var = tk.StringVar(value="valid")
        ttk.Combobox(self.form_frame, textvariable=self.status_var, values=["valid", "expired", "suspended", "revoked"], width=ENTRY_W, state="readonly").grid(row=2, column=3, padx=5, pady=4, sticky="w")
        tk.Label(self.form_frame, text="Address:", font=("Arial", 10)).grid(row=3, column=2, **LEFT)
        self.addr_entry = tk.Entry(self.form_frame, width=ENTRY_W + 10, font=("Arial", 10))
        self.addr_entry.grid(row=3, column=3, padx=5, pady=4, sticky="w")

    def get_fetch_all_query(self):
        return "SELECT license_number, CONCAT(first_name,' ',COALESCE(middle_name,''),' ',last_name) AS full_name, license_type, license_status, sex, date_of_birth, address FROM driver ORDER BY license_number"

    def get_search_query(self, term):
        q = "SELECT license_number, CONCAT(first_name,' ',COALESCE(middle_name,''),' ',last_name) AS full_name, license_type, license_status, sex, date_of_birth, address FROM driver WHERE license_number LIKE %s OR first_name LIKE %s OR last_name LIKE %s ORDER BY license_number"
        l = f"%{term}%"
        return q, (l, l, l)

    def format_row_data(self, row):
        return (row["license_number"], row["full_name"], row["license_type"], row["license_status"], row["sex"], row["date_of_birth"], row["address"])

    def populate_form(self, values):
        lic, full_name, lic_type, lic_status, sex, dob, addr = values
        self.lic_entry.config(state="normal"); self.lic_entry.delete(0, tk.END); self.lic_entry.insert(0, lic)
        parts = str(full_name).split()
        self.first_entry.delete(0, tk.END); self.mid_entry.delete(0, tk.END); self.last_entry.delete(0, tk.END)
        if len(parts) >= 1: self.first_entry.insert(0, parts[0])
        if len(parts) == 3: self.mid_entry.insert(0, parts[1]); self.last_entry.insert(0, parts[2])
        elif len(parts) == 2: self.last_entry.insert(0, parts[1])
        try: self.dob_entry.set_date(str(dob))
        except: pass
        self.sex_var.set(sex); self.type_var.set(lic_type); self.status_var.set(lic_status)
        self.addr_entry.delete(0, tk.END); self.addr_entry.insert(0, addr)
        self.set_edit_mode(lic)

    def clear_form(self):
        super().clear_form()
        for e in (self.lic_entry, self.first_entry, self.mid_entry, self.last_entry, self.addr_entry): e.delete(0, tk.END)
        self.sex_var.set("Male"); self.type_var.set("Non-Professional"); self.status_var.set("valid"); self.dob_entry.set_date(datetime.date.today())

    def get_pk_value(self): return self.lic_entry.get().strip()
    def enable_pk_field(self): self.lic_entry.config(state="normal")
    def disable_pk_field(self): self.lic_entry.config(state="disabled")

    def add_record(self):
        try:
            q = "INSERT INTO driver (license_number, first_name, middle_name, last_name, address, license_type, license_status, sex, date_of_birth) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            vals = (self.lic_entry.get().strip(), self.first_entry.get().strip(), self.mid_entry.get().strip() or None, self.last_entry.get().strip(), self.addr_entry.get().strip(), self.type_var.get(), self.status_var.get(), self.sex_var.get(), self.dob_entry.get_date().strftime("%Y-%m-%d"))
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Added!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_record(self):
        try:
            q = "UPDATE driver SET first_name=%s, middle_name=%s, last_name=%s, address=%s, license_type=%s, license_status=%s, sex=%s, date_of_birth=%s WHERE license_number=%s"
            vals = (self.first_entry.get().strip(), self.mid_entry.get().strip() or None, self.last_entry.get().strip(), self.addr_entry.get().strip(), self.type_var.get(), self.status_var.get(), self.sex_var.get(), self.dob_entry.get_date().strftime("%Y-%m-%d"), self.editing_id.get())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Updated!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

class VehicleManagement(BaseManagementWindow):
    def __init__(self, parent):
        columns = ("Plate No", "Make", "Model", "Year", "Color", "Type", "Owner")
        widths = [100, 120, 120, 60, 80, 120, 200]
        super().__init__(parent, "Vehicle Management", columns, widths, "vehicle", "plate_number")

    def setup_form_fields(self):
        LEFT = dict(padx=8, pady=4, sticky="e"); ENTRY_W = 28
        self.entries = {}
        for i, (l, k) in enumerate([("Plate No:", "plate"), ("Make:", "make"), ("Model:", "model"), ("Year:", "year"), ("Color:", "color"), ("Type:", "type"), ("Owner Lic:", "owner")]):
            tk.Label(self.form_frame, text=l, font=("Arial", 10)).grid(row=(i%4)+1, column=(i//4)*2, **LEFT)
            e = tk.Entry(self.form_frame, width=ENTRY_W); e.grid(row=(i%4)+1, column=(i//4)*2+1, padx=5, pady=4, sticky="w")
            self.entries[k] = e

    def get_fetch_all_query(self):
        return "SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type, CONCAT(d.first_name, ' ', d.last_name) AS owner FROM vehicle v JOIN driver d ON v.license_number = d.license_number ORDER BY v.plate_number"

    def get_search_query(self, term):
        q = "SELECT v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_type, CONCAT(d.first_name, ' ', d.last_name) AS owner FROM vehicle v JOIN driver d ON v.license_number = d.license_number WHERE v.plate_number LIKE %s OR v.make LIKE %s OR v.model LIKE %s ORDER BY v.plate_number"
        l = f"%{term}%"
        return q, (l, l, l)

    def format_row_data(self, row):
        return (row['plate_number'], row['make'], row['model'], row['year'], row['color'], row['vehicle_type'], row['owner'])

    def populate_form(self, values):
        plate, make, model, year, color, vtype, owner = values
        res = fetch_all("SELECT license_number FROM vehicle WHERE plate_number=%s", (plate,))
        lic = res[0]['license_number'] if res else ""
        self.entries['plate'].config(state="normal"); self.entries['plate'].delete(0, tk.END); self.entries['plate'].insert(0, plate)
        self.entries['make'].delete(0, tk.END); self.entries['make'].insert(0, make)
        self.entries['model'].delete(0, tk.END); self.entries['model'].insert(0, model)
        self.entries['year'].delete(0, tk.END); self.entries['year'].insert(0, year)
        self.entries['color'].delete(0, tk.END); self.entries['color'].insert(0, color)
        self.entries['type'].delete(0, tk.END); self.entries['type'].insert(0, vtype)
        self.entries['owner'].delete(0, tk.END); self.entries['owner'].insert(0, lic)
        self.set_edit_mode(plate)

    def clear_form(self):
        super().clear_form()
        for e in self.entries.values(): e.delete(0, tk.END)

    def get_pk_value(self): return self.entries['plate'].get().strip()
    def enable_pk_field(self): self.entries['plate'].config(state="normal")
    def disable_pk_field(self): self.entries['plate'].config(state="disabled")

    def add_record(self):
        try:
            q = "INSERT INTO vehicle (plate_number, make, model, year, color, vehicle_type, license_number, chassis_number, engine_number, registration_number, ownership) VALUES (%s,%s,%s,%s,%s,%s,%s,'TEMP','TEMP','TEMP','Owned')"
            vals = (self.entries['plate'].get().strip(), self.entries['make'].get().strip(), self.entries['model'].get().strip(), int(self.entries['year'].get() or 0), self.entries['color'].get().strip(), self.entries['type'].get().strip(), self.entries['owner'].get().strip())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Added!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_record(self):
        try:
            q = "UPDATE vehicle SET make=%s, model=%s, year=%s, color=%s, vehicle_type=%s, license_number=%s WHERE plate_number=%s"
            vals = (self.entries['make'].get().strip(), self.entries['model'].get().strip(), int(self.entries['year'].get() or 0), self.entries['color'].get().strip(), self.entries['type'].get().strip(), self.entries['owner'].get().strip(), self.editing_id.get())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Updated!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

class RegistrationManagement(BaseManagementWindow):
    def __init__(self, parent):
        columns = ("Reg No", "Plate No", "Reg Date", "Exp Date", "Status", "Owner", "Chassis", "Engine")
        widths = [80, 100, 100, 100, 80, 180, 100, 100]
        super().__init__(parent, "Registration Management", columns, widths, "vehicle_registration", "registration_number")

    def setup_form_fields(self):
        LEFT = dict(padx=8, pady=4, sticky="e"); ENTRY_W = 28
        self.entries = {}
        fields = [("Reg No:", "reg_no"), ("Plate No:", "plate"), ("Status:", "status"), ("Owner Lic:", "owner"), ("Chassis:", "chassis"), ("Engine:", "engine")]
        for i, (l, k) in enumerate(fields):
            tk.Label(self.form_frame, text=l, font=("Arial", 10)).grid(row=(i%3)+1, column=(i//3)*2, **LEFT)
            e = tk.Entry(self.form_frame, width=ENTRY_W); e.grid(row=(i%3)+1, column=(i//3)*2+1, padx=5, pady=4, sticky="w")
            self.entries[k] = e
        tk.Label(self.form_frame, text="Reg Date:", font=("Arial", 10)).grid(row=4, column=0, **LEFT)
        self.reg_date = DateEntry(self.form_frame, width=ENTRY_W-2, date_pattern="yyyy-mm-dd"); self.reg_date.grid(row=4, column=1, padx=5, pady=4, sticky="w")

    def get_fetch_all_query(self):
        return "SELECT vr.*, DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date, CONCAT(d.first_name, ' ', d.last_name) AS owner FROM vehicle_registration vr JOIN driver d ON vr.license_number = d.license_number ORDER BY vr.registration_date DESC"

    def get_search_query(self, term):
        q = "SELECT vr.*, DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date, CONCAT(d.first_name, ' ', d.last_name) AS owner FROM vehicle_registration vr JOIN driver d ON vr.license_number = d.license_number WHERE vr.registration_number LIKE %s OR vr.plate_number LIKE %s ORDER BY vr.registration_date DESC"
        l = f"%{term}%"
        return q, (l, l)

    def format_row_data(self, row):
        return (row['registration_number'], row['plate_number'], row['registration_date'], row['expiration_date'], row['registration_status'], row['owner'], row['chassis_number'], row['engine_number'])

    def populate_form(self, values):
        reg, plate, rdate, edate, status, owner, chassis, engine = values
        res = fetch_all("SELECT license_number FROM vehicle_registration WHERE registration_number=%s", (reg,))
        lic = res[0]['license_number'] if res else ""
        self.entries['reg_no'].config(state="normal"); self.entries['reg_no'].delete(0, tk.END); self.entries['reg_no'].insert(0, reg)
        self.entries['plate'].delete(0, tk.END); self.entries['plate'].insert(0, plate)
        self.entries['status'].delete(0, tk.END); self.entries['status'].insert(0, status)
        self.entries['owner'].delete(0, tk.END); self.entries['owner'].insert(0, lic)
        self.entries['chassis'].delete(0, tk.END); self.entries['chassis'].insert(0, chassis)
        self.entries['engine'].delete(0, tk.END); self.entries['engine'].insert(0, engine)
        try: self.reg_date.set_date(str(rdate))
        except: pass
        self.set_edit_mode(reg)

    def clear_form(self):
        super().clear_form()
        for e in self.entries.values(): e.delete(0, tk.END)
        self.reg_date.set_date(datetime.date.today())

    def get_pk_value(self): return self.entries['reg_no'].get().strip()
    def enable_pk_field(self): self.entries['reg_no'].config(state="normal")
    def disable_pk_field(self): self.entries['reg_no'].config(state="disabled")

    def add_record(self):
        try:
            q = "INSERT INTO vehicle_registration (registration_number, plate_number, registration_date, registration_status, license_number, chassis_number, engine_number) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            vals = (self.entries['reg_no'].get().strip(), self.entries['plate'].get().strip(), self.reg_date.get_date().strftime("%Y-%m-%d"), self.entries['status'].get().strip(), self.entries['owner'].get().strip(), self.entries['chassis'].get().strip(), self.entries['engine'].get().strip())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Added!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_record(self):
        try:
            q = "UPDATE vehicle_registration SET plate_number=%s, registration_date=%s, registration_status=%s, license_number=%s, chassis_number=%s, engine_number=%s WHERE registration_number=%s"
            vals = (self.entries['plate'].get().strip(), self.reg_date.get_date().strftime("%Y-%m-%d"), self.entries['status'].get().strip(), self.entries['owner'].get().strip(), self.entries['chassis'].get().strip(), self.entries['engine'].get().strip(), self.editing_id.get())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Updated!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

class ViolationManagement(BaseManagementWindow):
    def __init__(self, parent):
        columns = ("Violation ID", "Date", "Time", "Fine", "Status", "Type", "Driver", "Officer")
        widths = [100, 100, 80, 80, 100, 130, 180, 150]
        super().__init__(parent, "Violation Management", columns, widths, "violation_ticket", "violation_id")

    def setup_form_fields(self):
        LEFT = dict(padx=8, pady=4, sticky="e"); ENTRY_W = 28
        self.entries = {}
        fields = [("ID:", "id"), ("Driver Lic:", "lic"), ("Plate No:", "plate"), ("Time:", "time"), ("Fine:", "fine"), ("Status:", "status"), ("Officer:", "officer")]
        for i, (l, k) in enumerate(fields):
            tk.Label(self.form_frame, text=l, font=("Arial", 10)).grid(row=(i%4)+1, column=(i//4)*2, **LEFT)
            e = tk.Entry(self.form_frame, width=ENTRY_W); e.grid(row=(i%4)+1, column=(i//4)*2+1, padx=5, pady=4, sticky="w")
            self.entries[k] = e
        tk.Label(self.form_frame, text="Date:", font=("Arial", 10)).grid(row=4, column=2, **LEFT)
        self.date_entry = DateEntry(self.form_frame, width=ENTRY_W-2, date_pattern="yyyy-mm-dd"); self.date_entry.grid(row=4, column=3, padx=5, pady=4, sticky="w")

    def get_fetch_all_query(self):
        return "SELECT vt.*, CONCAT(vt.year,'-',vt.month,'-',vt.day) AS v_date, vth.violation_type, CONCAT(d.first_name,' ',d.last_name) AS driver FROM violation_ticket vt LEFT JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id LEFT JOIN driver d ON vt.license_number = d.license_number ORDER BY vt.year DESC, vt.month DESC, vt.day DESC"

    def get_search_query(self, term):
        q = "SELECT vt.*, CONCAT(vt.year,'-',vt.month,'-',vt.day) AS v_date, vth.violation_type, CONCAT(d.first_name,' ',d.last_name) AS driver FROM violation_ticket vt LEFT JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id LEFT JOIN driver d ON vt.license_number = d.license_number WHERE vt.violation_id LIKE %s OR vt.license_number LIKE %s ORDER BY vt.year DESC, vt.month DESC, vt.day DESC"
        l = f"%{term}%"
        return q, (l, l)

    def format_row_data(self, row):
        return (row['violation_id'], row['v_date'], row['time'], row['total_fine_amount'], row['ticket_status'], row['violation_type'], row['driver'], row['apprehending_officer'])

    def populate_form(self, values):
        vid, vdate, vtime, vfine, vstatus, vtype, vdriver, vofficer = values
        res = fetch_all("SELECT license_number, plate_number FROM violation_ticket WHERE violation_id=%s", (vid,))
        lic = res[0]['license_number'] if res else ""; plate = res[0]['plate_number'] if res else ""
        self.entries['id'].config(state="normal"); self.entries['id'].delete(0, tk.END); self.entries['id'].insert(0, vid)
        self.entries['lic'].delete(0, tk.END); self.entries['lic'].insert(0, lic)
        self.entries['plate'].delete(0, tk.END); self.entries['plate'].insert(0, plate)
        self.entries['time'].delete(0, tk.END); self.entries['time'].insert(0, vtime)
        self.entries['fine'].delete(0, tk.END); self.entries['fine'].insert(0, vfine)
        self.entries['status'].delete(0, tk.END); self.entries['status'].insert(0, vstatus)
        self.entries['officer'].delete(0, tk.END); self.entries['officer'].insert(0, vofficer)
        try: self.date_entry.set_date(str(vdate))
        except: pass
        self.set_edit_mode(vid)

    def clear_form(self):
        super().clear_form()
        for e in self.entries.values(): e.delete(0, tk.END)
        self.date_entry.set_date(datetime.date.today())

    def get_pk_value(self): return self.entries['id'].get().strip()
    def enable_pk_field(self): self.entries['id'].config(state="normal")
    def disable_pk_field(self): self.entries['id'].config(state="disabled")

    def add_record(self):
        try:
            d = self.date_entry.get_date()
            q = "INSERT INTO violation_ticket (violation_id, license_number, plate_number, year, month, day, time, total_fine_amount, ticket_status, apprehending_officer) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            vals = (self.entries['id'].get().strip(), self.entries['lic'].get().strip(), self.entries['plate'].get().strip(), d.year, d.month, d.day, self.entries['time'].get().strip(), float(self.entries['fine'].get() or 0), self.entries['status'].get().strip(), self.entries['officer'].get().strip())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Added!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

    def update_record(self):
        try:
            d = self.date_entry.get_date()
            q = "UPDATE violation_ticket SET license_number=%s, plate_number=%s, year=%s, month=%s, day=%s, time=%s, total_fine_amount=%s, ticket_status=%s, apprehending_officer=%s WHERE violation_id=%s"
            vals = (self.entries['lic'].get().strip(), self.entries['plate'].get().strip(), d.year, d.month, d.day, self.entries['time'].get().strip(), float(self.entries['fine'].get() or 0), self.entries['status'].get().strip(), self.entries['officer'].get().strip(), self.editing_id.get())
            ok, err = execute_query(q, vals)
            if ok: messagebox.showinfo("Success", "Updated!"); self.clear_form(); self.refresh_table()
            else: messagebox.showerror("Error", err)
        except Exception as e: messagebox.showerror("Error", str(e))

class ReportWindow:
    def __init__(self, parent, report_id, report_title):
        self.win = tk.Toplevel(parent)
        self.win.title(report_title)
        self.win.geometry("1100x700")
        self.report_id = report_id
        
        tk.Label(self.win, text=report_title, font=("Arial", 16, "bold")).pack(pady=10)
        
        # Filter Frame
        self.filter_frame = tk.LabelFrame(self.win, text="Report Filters", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.filter_frame.pack(pady=5, fill=tk.X, padx=10)
        
        self.inputs = {}
        self.setup_filters()
        
        # Action Buttons
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="RESET FILTERS / SHOW ALL", command=self.reset_filters, 
                  bg="#607D8B", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5).pack(side="left", padx=10)
        
        # Results Treeview
        self.tree_frame = tk.Frame(self.win)
        self.tree_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
        
        self.tree = ttk.Treeview(self.tree_frame, show="headings")
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.status_label = tk.Label(self.win, text="Ready", font=("Arial", 10, "italic"), fg="gray")
        self.status_label.pack(pady=5)
        
        self.generate() # Auto-populate on start
        
        tk.Button(self.win, text="CLOSE", command=self.win.destroy, bg="#555555", fg="white", font=("Arial", 11, "bold"), padx=30, pady=5).pack(pady=10)

    def setup_filters(self):
        L = dict(padx=5, pady=5, sticky="e")
        E = dict(padx=5, pady=5, sticky="w")
        
        def on_change(event=None):
            self.generate()

        if self.report_id == 1:
            tk.Label(self.filter_frame, text="License Type:").grid(row=0, column=0, **L)
            self.inputs['type'] = ttk.Combobox(self.filter_frame, values=["", "Student Permit", "Non-Professional", "Professional"], state="readonly")
            self.inputs['type'].grid(row=0, column=1, **E)
            self.inputs['type'].bind("<<ComboboxSelected>>", on_change)
            
            tk.Label(self.filter_frame, text="Status:").grid(row=0, column=2, **L)
            self.inputs['status'] = ttk.Combobox(self.filter_frame, values=["", "valid", "expired", "suspended", "revoked"], state="readonly")
            self.inputs['status'].grid(row=0, column=3, **E)
            self.inputs['status'].bind("<<ComboboxSelected>>", on_change)
            
            tk.Label(self.filter_frame, text="Sex:").grid(row=1, column=0, **L)
            self.inputs['sex'] = ttk.Combobox(self.filter_frame, values=["", "Male", "Female"], state="readonly")
            self.inputs['sex'].grid(row=1, column=1, **E)
            self.inputs['sex'].bind("<<ComboboxSelected>>", on_change)
            
            tk.Label(self.filter_frame, text="Age Range:").grid(row=1, column=2, **L)
            age_f = tk.Frame(self.filter_frame)
            age_f.grid(row=1, column=3, **E)
            self.inputs['age_min'] = tk.Entry(age_f, width=5)
            self.inputs['age_min'].pack(side="left")
            self.inputs['age_min'].bind("<KeyRelease>", on_change)
            tk.Label(age_f, text=" to ").pack(side="left")
            self.inputs['age_max'] = tk.Entry(age_f, width=5)
            self.inputs['age_max'].pack(side="left")
            self.inputs['age_max'].bind("<KeyRelease>", on_change)

        elif self.report_id == 2:
            tk.Label(self.filter_frame, text="Driver License Number:").grid(row=0, column=0, **L)
            self.inputs['lic'] = tk.Entry(self.filter_frame, width=30)
            self.inputs['lic'].grid(row=0, column=1, **E)
            self.inputs['lic'].bind("<KeyRelease>", on_change)

        elif self.report_id == 3:
            tk.Label(self.filter_frame, text="As of Date:").grid(row=0, column=0, **L)
            self.inputs['date'] = DateEntry(self.filter_frame, date_pattern="yyyy-mm-dd")
            self.inputs['date'].grid(row=0, column=1, **E)
            self.inputs['date'].bind("<<DateEntrySelected>>", on_change)

        elif self.report_id == 4:
            tk.Label(self.filter_frame, text="Showing drivers with expired or suspended licenses.").grid(row=0, column=0, columnspan=2, **E)

        elif self.report_id == 5:
            tk.Label(self.filter_frame, text="Driver License:").grid(row=0, column=0, **L)
            self.inputs['lic'] = tk.Entry(self.filter_frame, width=20)
            self.inputs['lic'].grid(row=0, column=1, **E)
            self.inputs['lic'].bind("<KeyRelease>", on_change)
            
            self.inputs['use_date'] = tk.BooleanVar(value=False)
            tk.Checkbutton(self.filter_frame, text="Enable Date Filter", variable=self.inputs['use_date'], command=on_change).grid(row=0, column=2, **L)
            
            tk.Label(self.filter_frame, text="Date Range:").grid(row=1, column=0, **L)
            dr_f = tk.Frame(self.filter_frame)
            dr_f.grid(row=1, column=1, **E)
            self.inputs['start'] = DateEntry(dr_f, date_pattern="yyyy-mm-dd")
            self.inputs['start'].pack(side="left")
            self.inputs['start'].bind("<<DateEntrySelected>>", on_change)
            tk.Label(dr_f, text=" to ").pack(side="left")
            self.inputs['end'] = DateEntry(dr_f, date_pattern="yyyy-mm-dd")
            self.inputs['end'].pack(side="left")
            self.inputs['end'].bind("<<DateEntrySelected>>", on_change)

        elif self.report_id == 6:
            tk.Label(self.filter_frame, text="Year:").grid(row=0, column=0, **L)
            # Fetch available years from database
            try:
                years_res = fetch_all("SELECT DISTINCT year FROM violation_ticket ORDER BY year DESC")
                years = ["All"] + [str(r['year']) for r in years_res]
                if len(years) == 1: years = ["All", str(datetime.date.today().year)]
            except:
                years = ["All", str(datetime.date.today().year)]
            
            self.inputs['year'] = ttk.Combobox(self.filter_frame, values=years, state="readonly", width=10)
            self.inputs['year'].set("All")
            self.inputs['year'].grid(row=0, column=1, **E)
            self.inputs['year'].bind("<<ComboboxSelected>>", on_change)

        elif self.report_id == 7:
            tk.Label(self.filter_frame, text="City or Region:").grid(row=0, column=0, **L)
            self.inputs['loc'] = tk.Entry(self.filter_frame, width=30)
            self.inputs['loc'].grid(row=0, column=1, **E)
            self.inputs['loc'].bind("<KeyRelease>", on_change)

    def reset_filters(self):
        for k, widget in self.inputs.items():
            if isinstance(widget, ttk.Combobox):
                if k == 'year': # Special case for Report 6
                    widget.set("All")
                else:
                    widget.set("")
            elif isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, DateEntry):
                widget.set_date(datetime.date.today())
            elif isinstance(widget, tk.BooleanVar):
                widget.set(False)
        self.generate()

    def generate(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        rows = []
        if self.report_id == 1:
            q = """
                SELECT license_number, CONCAT(first_name,' ',COALESCE(middle_name,''),' ',last_name) AS full_name,
                       license_type, license_status, sex,
                       YEAR(CURDATE()) - YEAR(date_of_birth) - (DATE_FORMAT(CURDATE(),'%m%d') < DATE_FORMAT(date_of_birth,'%m%d')) AS age
                FROM driver WHERE 1=1
            """
            p = []
            if self.inputs['type'].get(): q += " AND license_type=%s"; p.append(self.inputs['type'].get())
            if self.inputs['status'].get(): q += " AND license_status=%s"; p.append(self.inputs['status'].get())
            if self.inputs['sex'].get(): q += " AND sex=%s"; p.append(self.inputs['sex'].get())
            if self.inputs['age_min'].get(): q += " AND (YEAR(CURDATE()) - YEAR(date_of_birth)) >= %s"; p.append(self.inputs['age_min'].get())
            if self.inputs['age_max'].get(): q += " AND (YEAR(CURDATE()) - YEAR(date_of_birth)) <= %s"; p.append(self.inputs['age_max'].get())
            
            cols = ("License No", "Full Name", "Type", "Status", "Sex", "Age")
            self.setup_tree(cols, [120, 250, 150, 100, 80, 60])
            rows = fetch_all(q, p)

        elif self.report_id == 2:
            lic = self.inputs['lic'].get().strip()
            q = "SELECT plate_number, make, model, year, color, vehicle_type FROM vehicle WHERE 1=1"
            p = []
            if lic: q += " AND license_number LIKE %s"; p.append(f"%{lic}%")
            cols = ("Plate No", "Make", "Model", "Year", "Color", "Type")
            self.setup_tree(cols, [100, 120, 120, 80, 100, 150])
            rows = fetch_all(q, p)

        elif self.report_id == 3:
            as_of = self.inputs['date'].get_date().strftime("%Y-%m-%d")
            q = """
                SELECT vr.registration_number, vr.plate_number, v.make, v.model, vr.registration_date,
                       DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) AS expiration_date,
                       CONCAT(d.first_name, ' ', d.last_name) AS owner_name
                FROM vehicle_registration vr
                JOIN vehicle v ON vr.plate_number = v.plate_number
                JOIN driver d ON vr.license_number = d.license_number
                WHERE DATE_ADD(vr.registration_date, INTERVAL 1 YEAR) < %s OR vr.registration_status = 'expired'
            """
            cols = ("Reg No", "Plate No", "Make/Model", "Reg Date", "Exp Date", "Owner")
            self.setup_tree(cols, [100, 100, 180, 120, 120, 200])
            rows = fetch_all(q, (as_of,))

        elif self.report_id == 4:
            q = "SELECT license_number, CONCAT(first_name,' ',last_name) AS name, license_type, license_status FROM driver WHERE license_status IN ('expired', 'suspended') ORDER BY license_status"
            cols = ("License No", "Name", "Type", "Status")
            self.setup_tree(cols, [150, 250, 150, 120])
            rows = fetch_all(q)

        elif self.report_id == 5:
            lic = self.inputs['lic'].get().strip()
            use_date = self.inputs['use_date'].get()
            q = """
                SELECT vt.violation_id, CONCAT(vt.year,'-',vt.month,'-',vt.day) AS v_date, vt.total_fine_amount, vt.ticket_status,
                       GROUP_CONCAT(vth.violation_type SEPARATOR ', ') AS types
                FROM violation_ticket vt
                LEFT JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id
                WHERE 1=1
            """
            p = []
            if lic: q += " AND vt.license_number LIKE %s"; p.append(f"%{lic}%")
            if use_date:
                sd = self.inputs['start'].get_date().strftime("%Y-%m-%d")
                ed = self.inputs['end'].get_date().strftime("%Y-%m-%d")
                # Using %M for full month name (e.g., 'March')
                q += " AND STR_TO_DATE(CONCAT(vt.year,'-',vt.month,'-',vt.day), '%Y-%M-%d') BETWEEN %s AND %s"
                p.extend([sd, ed])
            q += " GROUP BY vt.violation_id"
            cols = ("Violation ID", "Date", "Fine", "Status", "Types")
            self.setup_tree(cols, [120, 120, 100, 100, 400])
            rows = fetch_all(q, p)

        elif self.report_id == 6:
            yr = self.inputs['year'].get().strip()
            q = """
                SELECT vt.year, vth.violation_type, COUNT(*) AS total_tickets, SUM(vt.total_fine_amount) AS total_fines
                FROM violation_ticket vt
                JOIN violation_ticket_has_type vth ON vt.violation_id = vth.violation_id
                WHERE 1=1
            """
            p = []
            if yr and yr != "All": q += " AND vt.year = %s"; p.append(yr)
            q += " GROUP BY vt.year, vth.violation_type ORDER BY vt.year DESC, total_tickets DESC"
            cols = ("Year", "Violation Type", "Total Tickets", "Total Fines")
            self.setup_tree(cols, [80, 400, 150, 150])
            rows = fetch_all(q, p)

        elif self.report_id == 7:
            loc = self.inputs['loc'].get().strip()
            q = """
                SELECT DISTINCT v.plate_number, v.make, v.model, CONCAT(d.first_name, ' ', d.last_name) AS owner, d.address
                FROM vehicle v JOIN driver d ON v.license_number = d.license_number
                JOIN violation_ticket vt ON vt.plate_number = v.plate_number
                WHERE 1=1
            """
            p = []
            if loc: q += " AND d.address LIKE %s"; p.append(f"%{loc}%")
            cols = ("Plate No", "Make/Model", "Owner", "Driver Address")
            self.setup_tree(cols, [100, 180, 200, 400])
            rows = fetch_all(q, p)

        for r in rows:
            if self.report_id == 1: self.tree.insert("", tk.END, values=(r['license_number'], r['full_name'], r['license_type'], r['license_status'], r['sex'], r['age']))
            elif self.report_id == 2: self.tree.insert("", tk.END, values=(r['plate_number'], r['make'], r['model'], r['year'], r['color'], r['vehicle_type']))
            elif self.report_id == 3: self.tree.insert("", tk.END, values=(r['registration_number'], r['plate_number'], f"{r['make']} {r['model']}", r['registration_date'], r['expiration_date'], r['owner_name']))
            elif self.report_id == 4: self.tree.insert("", tk.END, values=(r['license_number'], r['name'], r['license_type'], r['license_status']))
            elif self.report_id == 5: self.tree.insert("", tk.END, values=(r['violation_id'], r['v_date'], r['total_fine_amount'], r['ticket_status'], r['types']))
            elif self.report_id == 6: self.tree.insert("", tk.END, values=(r['year'], r['violation_type'], r['total_tickets'], f"{float(r['total_fines'] or 0):,.2f}"))
            elif self.report_id == 7: self.tree.insert("", tk.END, values=(r['plate_number'], f"{r['make']} {r['model']}", r['owner'], r['address']))

        if rows:
            self.status_label.config(text=f"Found {len(rows)} record(s)", fg="#4CAF50")
        else:
            self.status_label.config(text="No records found.", fg="#f44336")

    def setup_tree(self, columns, widths):
        self.tree["columns"] = columns
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

class LTOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LTO Management System V2")
        self.root.geometry("1000x700")
        
        # Style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        tk.Label(root, text="LTO Information Management System", font=("Arial", 22, "bold"), pady=30).pack()
        
        f = tk.Frame(root)
        f.pack(pady=20)
        
        menu_items = [
            ("Driver Management", "#4CAF50", lambda: DriverManagement(self.root)),
            ("Vehicle Management", "#2196F3", lambda: VehicleManagement(self.root)),
            ("Registration Management", "#FF9800", lambda: RegistrationManagement(self.root)),
            ("Violation Management", "#9C27B0", lambda: ViolationManagement(self.root)),
            ("Reports System", "#009688", self.reports_menu),
            ("Exit System", "#f44336", root.quit)
        ]
        
        for i, (text, color, cmd) in enumerate(menu_items):
            tk.Button(f, text=text, command=cmd, width=28, height=2, bg=color, fg="white", font=("Arial", 11, "bold"), relief="flat", activebackground=color).grid(row=i//2, column=i%2, padx=15, pady=15)

    def reports_menu(self):
        win = tk.Toplevel(self.root); win.title("LTO Reports System"); win.geometry("800x600")
        tk.Label(win, text="Available Reports", font=("Arial", 18, "bold")).pack(pady=20)
        
        reps = [
            ("1. Drivers filtered by type, status, age, sex", 1),
            ("2. Vehicles owned by a driver", 2),
            ("3. Vehicles with expired registrations", 3),
            ("4. Drivers with expired/suspended licenses", 4),
            ("5. Violations by driver within date range", 5),
            ("6. Total violations per type for a year", 6),
            ("7. Vehicles involved in violations by location", 7)
        ]
        
        for text, rid in reps:
            tk.Button(win, text=text, command=lambda r=rid, t=text: ReportWindow(self.root, r, t),
                      width=70, anchor="w", font=("Arial", 10), padx=20, pady=8, bg="#f8f9fa").pack(pady=5)
            
        tk.Button(win, text="CLOSE", command=win.destroy, bg="#f44336", fg="white", font=("Arial", 10, "bold"), padx=30, pady=10).pack(pady=20)

    # run_report is no longer needed as ReportWindow handles it

if __name__ == "__main__":
    root = tk.Tk(); app = LTOApp(root); root.mainloop()
