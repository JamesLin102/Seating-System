import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import json
import random
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

class ExamSeatingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Exam Seating System")
        self.root.geometry("1200x800")
        
        # Data storage
        self.rows = 6
        self.cols = 8
        self.disabled_seats = set()
        self.students = []
        self.seating_arrangement = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Control panel (left side)
        control_frame = tk.Frame(self.root, width=320, bg='#f0f0f0')
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # Button width constant
        BTN_WIDTH = 25
        
        # Title
        tk.Label(control_frame, text="Exam Seating System", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0', fg='#333').pack(pady=15)
        
        # Classroom settings
        tk.Label(control_frame, text="Classroom Settings", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(10,5))
        
        size_frame = tk.Frame(control_frame, bg='#f0f0f0')
        size_frame.pack(pady=5)
        tk.Label(size_frame, text="Rows:", bg='#f0f0f0', width=9, anchor='e').pack(side=tk.LEFT)
        self.rows_entry = tk.Entry(size_frame, width=6)
        self.rows_entry.insert(0, str(self.rows))
        self.rows_entry.pack(side=tk.LEFT, padx=3)
        
        tk.Label(size_frame, text="Cols:", bg='#f0f0f0', width=9, anchor='e').pack(side=tk.LEFT)
        self.cols_entry = tk.Entry(size_frame, width=6)
        self.cols_entry.insert(0, str(self.cols))
        self.cols_entry.pack(side=tk.LEFT, padx=3)
        
        tk.Button(control_frame, text="Set Classroom Size", command=self.set_classroom_size, 
                 bg='#4CAF50', fg='white', width=BTN_WIDTH).pack(pady=5)
        
        tk.Label(control_frame, text="Click seats to enable/disable", bg='#f0f0f0', 
                font=('Arial', 9, 'italic'), fg='#666').pack(pady=3)
        
        # Classroom management
        tk.Label(control_frame, text="Classroom Management", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(15,5))
        
        tk.Button(control_frame, text="💾 Save Classroom", command=self.save_classroom,
                 bg='#9C27B0', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        tk.Button(control_frame, text="📂 Load Classroom", command=self.load_classroom,
                 bg='#673AB7', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        # Student info
        tk.Label(control_frame, text="Student Information", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(15,5))
        
        self.student_count_label = tk.Label(control_frame, text="Students Loaded: 0", 
                                           bg='#f0f0f0', font=('Arial', 10))
        self.student_count_label.pack(pady=5)
        
        tk.Button(control_frame, text="📋 Load Student List", command=self.load_students,
                 bg='#2196F3', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        # Seating arrangement
        tk.Label(control_frame, text="Seating Arrangement", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(15,5))
        
        tk.Button(control_frame, text="🎲 Random Arrangement", command=self.arrange_seats,
                 bg='#FF9800', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        tk.Button(control_frame, text="🗑️ Clear Arrangement", command=self.clear_arrangement,
                 bg='#f44336', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        # Export
        tk.Label(control_frame, text="Export", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(15,5))
        
        tk.Button(control_frame, text="📄 Export to PDF", command=self.export_pdf,
                 bg='#E91E63', fg='white', width=BTN_WIDTH).pack(pady=3)
        
        # Legend
        tk.Label(control_frame, text="Legend", 
                font=('Arial', 13, 'bold'), bg='#f0f0f0').pack(pady=(20,5))
        
        legend_frame = tk.Frame(control_frame, bg='#f0f0f0')
        legend_frame.pack(pady=5)
        
        colors = [
            ("Available", "#90EE90"),
            ("Disabled", "#FFB6C6"),
            ("Assigned", "#87CEEB")
        ]
        for label, color in colors:
            f = tk.Frame(legend_frame, bg='#f0f0f0')
            f.pack(pady=2)
            tk.Label(f, width=3, bg=color, relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT)
            tk.Label(f, text=label, bg='#f0f0f0', width=10, anchor='w').pack(side=tk.LEFT, padx=5)
        
        # Canvas for seating chart (right side)
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_classroom()
        
    def set_classroom_size(self):
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())
            if new_rows < 1 or new_cols < 1 or new_rows > 20 or new_cols > 20:
                messagebox.showerror("Error", "Rows and columns must be between 1-20")
                return
            self.rows = new_rows
            self.cols = new_cols
            self.disabled_seats.clear()
            self.seating_arrangement.clear()
            self.draw_classroom()
            messagebox.showinfo("Success", f"Classroom size set to {self.rows} × {self.cols}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def draw_classroom(self):
        self.canvas.delete("all")
        
        # Calculate dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width < 100:
            canvas_width = 800
        if canvas_height < 100:
            canvas_height = 600
            
        # Stage at the top
        stage_height = 60
        self.canvas.create_rectangle(50, 20, canvas_width-50, 20+stage_height, 
                                     fill='#FFE4B5', outline='black', width=2)
        self.canvas.create_text(canvas_width//2, 50, text="STAGE", 
                               font=('Arial', 16, 'bold'))
        
        # Calculate seat dimensions
        margin = 50
        available_width = canvas_width - 2*margin
        available_height = canvas_height - stage_height - 3*margin
        
        seat_width = min(available_width // self.cols, 80)
        seat_height = min(available_height // self.rows, 60)
        
        start_x = (canvas_width - seat_width * self.cols) // 2
        start_y = stage_height + 2*margin
        
        # Draw seats
        self.seat_buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = start_x + col * seat_width
                y1 = start_y + row * seat_height
                x2 = x1 + seat_width - 5
                y2 = y1 + seat_height - 5
                
                seat_id = f"{row},{col}"
                
                # Determine color
                if seat_id in self.disabled_seats:
                    color = "#FFB6C6"
                elif seat_id in self.seating_arrangement:
                    color = "#87CEEB"
                else:
                    color = "#90EE90"
                
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                   fill=color, outline='black', width=1)
                
                # Display student name if assigned
                text = ""
                if seat_id in self.seating_arrangement:
                    text = self.seating_arrangement[seat_id]
                else:
                    text = f"R{row+1}C{col+1}"
                
                text_id = self.canvas.create_text((x1+x2)//2, (y1+y2)//2, 
                                                 text=text, font=('Arial', 9))
                
                self.seat_buttons[seat_id] = (rect, text_id)
                
                # Bind click event
                self.canvas.tag_bind(rect, '<Button-1>', 
                                    lambda e, s=seat_id: self.toggle_seat(s))
                self.canvas.tag_bind(text_id, '<Button-1>', 
                                    lambda e, s=seat_id: self.toggle_seat(s))
    
    def toggle_seat(self, seat_id):
        if seat_id in self.seating_arrangement:
            messagebox.showinfo("Notice", "Please clear arrangement before modifying seats")
            return
            
        if seat_id in self.disabled_seats:
            self.disabled_seats.remove(seat_id)
        else:
            self.disabled_seats.add(seat_id)
        self.draw_classroom()
    
    def load_students(self):
        filename = filedialog.askopenfilename(
            title="Select Student List",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            df = pd.read_csv(filename, encoding='utf-8')
        except:
            try:
                df = pd.read_csv(filename, encoding='big5')
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read file: {str(e)}")
                return
        
        # Show column selector
        selector = ColumnSelector(self.root, df.columns.tolist())
        self.root.wait_window(selector.dialog)
        
        if selector.selected_column:
            self.students = df[selector.selected_column].dropna().tolist()
            self.student_count_label.config(text=f"Students Loaded: {len(self.students)}")
            messagebox.showinfo("Success", f"Successfully loaded {len(self.students)} students")
        
    def arrange_seats(self):
        if not self.students:
            messagebox.showwarning("Warning", "Please load student list first")
            return
        
        # Get available seats
        available_seats = []
        for row in range(self.rows):
            for col in range(self.cols):
                seat_id = f"{row},{col}"
                if seat_id not in self.disabled_seats:
                    available_seats.append(seat_id)
        
        if len(self.students) > len(available_seats):
            messagebox.showerror("Error", 
                               f"Number of students ({len(self.students)}) exceeds available seats ({len(available_seats)})")
            return
        
        # Random arrangement
        shuffled_students = self.students.copy()
        random.shuffle(shuffled_students)
        
        self.seating_arrangement.clear()
        for i, student in enumerate(shuffled_students):
            self.seating_arrangement[available_seats[i]] = student
        
        self.draw_classroom()
        messagebox.showinfo("Success", "Seating arrangement completed")
    
    def clear_arrangement(self):
        self.seating_arrangement.clear()
        self.draw_classroom()
    
    def save_classroom(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            data = {
                'rows': self.rows,
                'cols': self.cols,
                'disabled_seats': list(self.disabled_seats)
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Success", "Classroom configuration saved")
    
    def load_classroom(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.rows = data['rows']
            self.cols = data['cols']
            self.disabled_seats = set(data['disabled_seats'])
            self.rows_entry.delete(0, tk.END)
            self.rows_entry.insert(0, str(self.rows))
            self.cols_entry.delete(0, tk.END)
            self.cols_entry.insert(0, str(self.cols))
            self.seating_arrangement.clear()
            self.draw_classroom()
            messagebox.showinfo("Success", "Classroom configuration loaded")
    
    def export_pdf(self):
        if not self.seating_arrangement:
            messagebox.showwarning("Warning", "Please arrange seats first")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filename:
            return
        
        try:
            # Register Chinese font (try common system fonts)
            try:
                pdfmetrics.registerFont(TTFont('Chinese', 'mingliu.ttc'))
                font_name = 'Chinese'
            except:
                try:
                    pdfmetrics.registerFont(TTFont('Chinese', 'kaiu.ttf'))
                    font_name = 'Chinese'
                except:
                    font_name = 'Helvetica'
            
            c = canvas.Canvas(filename, pagesize=landscape(A4))
            width, height = landscape(A4)
            
            # Title
            c.setFont(font_name, 20)
            c.drawCentredString(width/2, height - 40, "Exam Seating Chart")
            
            # Stage
            stage_y = height - 100
            c.setFillColorRGB(1, 0.89, 0.71)
            c.rect(50, stage_y-30, width-100, 30, fill=1)
            c.setFillColorRGB(0, 0, 0)
            c.setFont(font_name, 14)
            c.drawCentredString(width/2, stage_y-20, "STAGE")
            
            # Calculate seat positions
            seat_width = min((width - 100) / self.cols, 60)
            seat_height = min((stage_y - 150) / self.rows, 50)
            
            start_x = (width - seat_width * self.cols) / 2
            start_y = stage_y - 80
            
            c.setFont(font_name, 9)
            
            # Draw seats
            for row in range(self.rows):
                for col in range(self.cols):
                    seat_id = f"{row},{col}"
                    
                    if seat_id in self.disabled_seats:
                        continue
                    
                    x = start_x + col * seat_width
                    y = start_y - row * seat_height
                    
                    # Draw rectangle
                    if seat_id in self.seating_arrangement:
                        c.setFillColorRGB(0.53, 0.81, 0.92)
                    else:
                        c.setFillColorRGB(0.56, 0.93, 0.56)
                    
                    c.rect(x, y, seat_width-5, seat_height-5, fill=1)
                    c.setFillColorRGB(0, 0, 0)
                    c.rect(x, y, seat_width-5, seat_height-5, fill=0)
                    
                    # Draw text
                    text = self.seating_arrangement.get(seat_id, f"R{row+1}C{col+1}")
                    c.drawCentredString(x + (seat_width-5)/2, y + (seat_height-5)/2 - 3, text)
            
            c.save()
            messagebox.showinfo("Success", f"Seating chart exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting PDF:\n{str(e)}")

class ColumnSelector:
    def __init__(self, parent, columns):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Student Name Column")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.selected_column = None
        
        tk.Label(self.dialog, text="Please select the column with student names:", 
                font=('Arial', 12)).pack(pady=10)
        
        listbox_frame = tk.Frame(self.dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, 
                                  font=('Arial', 11))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        for col in columns:
            self.listbox.insert(tk.END, col)
        
        if columns:
            self.listbox.selection_set(0)
        
        tk.Button(self.dialog, text="Confirm", command=self.confirm, 
                 bg='#4CAF50', fg='white', font=('Arial', 11)).pack(pady=10)
        
        self.listbox.bind('<Double-Button-1>', lambda e: self.confirm())
        
    def confirm(self):
        selection = self.listbox.curselection()
        if selection:
            self.selected_column = self.listbox.get(selection[0])
        self.dialog.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExamSeatingSystem(root)
    root.mainloop()