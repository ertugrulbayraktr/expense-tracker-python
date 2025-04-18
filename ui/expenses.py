"""
Expense management UI components for the expense tracking system.
This module provides UI components for adding, editing, and managing expenses.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
import os
import csv
from tkinter import filedialog
from tkcalendar import DateEntry
from .base import BaseFrame, ScrollableFrame, Tooltip
from models.expense import Expense
from models.category import Category
from utils.analysis import export_expenses_to_csv

class ExpensesFrame(BaseFrame):
    """Main frame for managing expenses."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new ExpensesFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize variables
        self.expenses = []
        self.filtered_expenses = []
        self.categories_dict = {}
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_filter = "all"
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the expense management widgets."""
        # Main container with navbar and content
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Create top navbar
        self._create_navbar(container)
        
        # Create content area with sidebar and main panel
        content = ttk.Frame(container)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=4)
        
        # Create sidebar
        self._create_sidebar(content)
        
        # Create main panel
        self.main_panel = ttk.Frame(content)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)
        
        # Show expenses list by default
        self._show_expenses_list()
    
    def _create_navbar(self, parent):
        """Create the top navigation bar."""
        navbar = ttk.Frame(parent, style="Card.TFrame", padding=10)
        navbar.grid(row=0, column=0, sticky="ew")
        
        # App title and navigation
        title_frame = ttk.Frame(navbar)
        title_frame.pack(side="left")
        
        dashboard_btn = ttk.Button(title_frame, text="Dashboard", width=10,
                                  command=lambda: self.controller.show_frame("DashboardFrame"))
        dashboard_btn.pack(side="left", padx=5)
        
        ttk.Label(title_frame, text=">", style="Title.TLabel").pack(side="left", padx=5)
        
        title_label = ttk.Label(title_frame, text="Expenses", style="Title.TLabel")
        title_label.pack(side="left", padx=5)
        
        # User info and settings
        user_frame = ttk.Frame(navbar)
        user_frame.pack(side="right", padx=10)
        
        self.user_var = tk.StringVar(value="Welcome, User")
        user_label = ttk.Label(user_frame, textvariable=self.user_var)
        user_label.pack(side="left", padx=5)
    
    def _create_sidebar(self, parent):
        """Create the sidebar with filter options."""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        
        # Filter section
        filter_label = ttk.Label(sidebar, text="Filter Expenses", font=("Helvetica", 12, "bold"))
        filter_label.pack(anchor="w", pady=(0, 10))
        
        # Date filters
        date_frame = ttk.LabelFrame(sidebar, text="Date Range")
        date_frame.pack(fill="x", pady=5)
        
        # Create radio buttons for date filters
        self.filter_var = tk.StringVar(value="all")
        
        all_radio = ttk.Radiobutton(date_frame, text="All Time", value="all", 
                                   variable=self.filter_var, command=self._apply_filters)
        all_radio.pack(anchor="w", padx=5, pady=2)
        
        current_month_radio = ttk.Radiobutton(date_frame, text="Current Month", value="current_month", 
                                            variable=self.filter_var, command=self._apply_filters)
        current_month_radio.pack(anchor="w", padx=5, pady=2)
        
        last_month_radio = ttk.Radiobutton(date_frame, text="Last Month", value="last_month", 
                                         variable=self.filter_var, command=self._apply_filters)
        last_month_radio.pack(anchor="w", padx=5, pady=2)
        
        custom_radio = ttk.Radiobutton(date_frame, text="Custom Range", value="custom", 
                                     variable=self.filter_var, command=self._apply_filters)
        custom_radio.pack(anchor="w", padx=5, pady=2)
        
        # Custom date range
        custom_frame = ttk.Frame(date_frame)
        custom_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(custom_frame, text="From:").grid(row=0, column=0, sticky="w")
        self.start_date = DateEntry(custom_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(custom_frame, text="To:").grid(row=1, column=0, sticky="w")
        self.end_date = DateEntry(custom_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=1, column=1, padx=5, pady=2)
        
        apply_btn = ttk.Button(custom_frame, text="Apply", command=self._apply_filters)
        apply_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Category filter
        cat_frame = ttk.LabelFrame(sidebar, text="Categories")
        cat_frame.pack(fill="x", pady=10)
        
        self.category_var = tk.StringVar(value="all")
        
        all_cat_radio = ttk.Radiobutton(cat_frame, text="All Categories", value="all", 
                                       variable=self.category_var, command=self._apply_filters)
        all_cat_radio.pack(anchor="w", padx=5, pady=2)
        
        # Category list will be populated in refresh_data
        self.category_frame = ttk.Frame(cat_frame)
        self.category_frame.pack(fill="x", padx=5, pady=5)
        
        # Type filter
        type_frame = ttk.LabelFrame(sidebar, text="Transaction Type")
        type_frame.pack(fill="x", pady=5)
        
        self.type_var = tk.StringVar(value="all")
        
        all_type_radio = ttk.Radiobutton(type_frame, text="All Transactions", value="all", 
                                       variable=self.type_var, command=self._apply_filters)
        all_type_radio.pack(anchor="w", padx=5, pady=2)
        
        expense_radio = ttk.Radiobutton(type_frame, text="Expenses Only", value="expense", 
                                      variable=self.type_var, command=self._apply_filters)
        expense_radio.pack(anchor="w", padx=5, pady=2)
        
        income_radio = ttk.Radiobutton(type_frame, text="Income Only", value="income", 
                                     variable=self.type_var, command=self._apply_filters)
        income_radio.pack(anchor="w", padx=5, pady=2)
        
        # Add separator
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)
        
        # Export section
        export_label = ttk.Label(sidebar, text="Export Data", font=("Helvetica", 12, "bold"))
        export_label.pack(anchor="w", pady=(10, 5))
        
        # Export button - Tamamen yeniden oluşturuyoruz
        export_frame = ttk.Frame(sidebar)
        export_frame.pack(fill="x", pady=2)
        export_btn = ttk.Button(export_frame, text="Export to CSV", command=lambda: self._export_to_csv())
        export_btn.pack(fill="x")
        
        # Add expense button
        add_btn = ttk.Button(sidebar, text="Add New Expense", style="Primary.TButton",
                           command=self.show_add_expense_dialog)
        add_btn.pack(pady=10, fill="x")
    
    def _show_expenses_list(self):
        """Show the expenses list in the main panel."""
        # Clear the main panel
        for widget in self.main_panel.winfo_children():
            widget.destroy()
        
        # Create scrollable container
        scrollable = ScrollableFrame(self.main_panel)
        scrollable.pack(side="top", fill="both", expand=True)
        container = scrollable.scrollable_frame
        
        # Add header with title and search
        header_frame = ttk.Frame(container)
        header_frame.pack(pady=10, fill="x", padx=20)
        
        title_label = ttk.Label(header_frame, text="Manage Expenses", style="Title.TLabel")
        title_label.pack(side="left")
        
        # Search box
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side="right")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self._apply_filters())
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self._apply_filters)
        search_btn.pack(side="left")
        
        # Create expenses table
        table_frame = ttk.Frame(container, style="Card.TFrame", padding=10)
        table_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        # Table headers
        headers_frame = ttk.Frame(table_frame)
        headers_frame.pack(fill="x", pady=(0, 5))
        
        # Configure columns
        headers_frame.grid_columnconfigure(0, weight=1)  # Date
        headers_frame.grid_columnconfigure(1, weight=2)  # Description
        headers_frame.grid_columnconfigure(2, weight=1)  # Category
        headers_frame.grid_columnconfigure(3, weight=1)  # Amount
        headers_frame.grid_columnconfigure(4, weight=0)  # Actions
        
        # Add headers
        ttk.Label(headers_frame, text="Date", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ttk.Label(headers_frame, text="Description", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(headers_frame, text="Category", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        ttk.Label(headers_frame, text="Amount", font=("Helvetica", 10, "bold")).grid(row=0, column=3, sticky="w", padx=5)
        ttk.Label(headers_frame, text="Actions", font=("Helvetica", 10, "bold")).grid(row=0, column=4, sticky="w", padx=5)
        
        ttk.Separator(table_frame, orient="horizontal").pack(fill="x", pady=5)
        
        # Expenses container
        expenses_container = ttk.Frame(table_frame)
        expenses_container.pack(fill="both", expand=True)
        
        # Configure columns for expenses
        expenses_container.grid_columnconfigure(0, weight=1)  # Date
        expenses_container.grid_columnconfigure(1, weight=2)  # Description
        expenses_container.grid_columnconfigure(2, weight=1)  # Category
        expenses_container.grid_columnconfigure(3, weight=1)  # Amount
        expenses_container.grid_columnconfigure(4, weight=0)  # Actions
        
        # Add expenses rows
        if self.filtered_expenses:
            for i, expense in enumerate(self.filtered_expenses):
                row_frame = ttk.Frame(expenses_container)
                row_frame.grid(row=i, column=0, columnspan=5, sticky="ew", pady=2)
                
                # Configure row columns
                row_frame.grid_columnconfigure(0, weight=1)
                row_frame.grid_columnconfigure(1, weight=2)
                row_frame.grid_columnconfigure(2, weight=1)
                row_frame.grid_columnconfigure(3, weight=1)
                row_frame.grid_columnconfigure(4, weight=0)
                
                # Date
                ttk.Label(row_frame, text=expense.date).grid(row=0, column=0, sticky="w", padx=5)
                
                # Description
                desc_text = expense.description
                if len(desc_text) > 30:
                    desc_text = desc_text[:27] + "..."
                ttk.Label(row_frame, text=desc_text).grid(row=0, column=1, sticky="w", padx=5)
                
                # Category
                category_name = "Unknown"
                if expense.category_id in self.categories_dict:
                    category_name = self.categories_dict[expense.category_id].name
                ttk.Label(row_frame, text=category_name).grid(row=0, column=2, sticky="w", padx=5)
                
                # Amount
                amount_text = f"${expense.amount:.2f}"
                amount_color = "#2ecc71" if expense.is_income else "#e74c3c"
                amount_label = ttk.Label(row_frame, text=amount_text, foreground=amount_color)
                amount_label.grid(row=0, column=3, sticky="w", padx=5)
                
                # Actions
                actions_frame = ttk.Frame(row_frame)
                actions_frame.grid(row=0, column=4, sticky="e", padx=5)
                
                edit_btn = ttk.Button(actions_frame, text="Edit", width=5,
                                    command=lambda e=expense: self._show_edit_expense_dialog(e))
                edit_btn.pack(side="left", padx=2)
                
                delete_btn = ttk.Button(actions_frame, text="Delete", width=5,
                                      command=lambda e=expense: self._confirm_delete_expense(e))
                delete_btn.pack(side="left", padx=2)
                
                # Add separator
                if i < len(self.filtered_expenses) - 1:
                    ttk.Separator(expenses_container, orient="horizontal").grid(
                        row=i+1, column=0, columnspan=5, sticky="ew", pady=5)
        else:
            no_data_label = ttk.Label(expenses_container, text="No expenses found matching your filters",
                                    font=("Helvetica", 12))
            no_data_label.pack(pady=20)
        
        # Pagination (simplified)
        pagination_frame = ttk.Frame(container)
        pagination_frame.pack(pady=10, fill="x", padx=20)
        
        # Just show count for now
        count_label = ttk.Label(pagination_frame, 
                              text=f"Showing {len(self.filtered_expenses)} of {len(self.expenses)} expenses")
        count_label.pack(side="left")
        
        # Add refresh button
        refresh_btn = ttk.Button(pagination_frame, text="Refresh", width=10,
                               command=self.refresh_data)
        refresh_btn.pack(side="right")

    def _apply_filters(self):
        """Apply filters to the expense list."""
        if not self.expenses:
            self.filtered_expenses = []
            self._show_expenses_list()
            return
        
        # Get filter values
        date_filter = self.filter_var.get()
        category_filter = self.category_var.get()
        type_filter = self.type_var.get()
        search_text = self.search_var.get().lower()
        
        # Start with all expenses
        filtered = self.expenses
        
        # Apply date filter
        now = datetime.now()
        
        if date_filter == "current_month":
            # Current month
            current_month = now.strftime("%Y-%m")
            filtered = [e for e in filtered if e.date and e.date.startswith(current_month)]
        
        elif date_filter == "last_month":
            # Last month
            if now.month == 1:
                last_month = f"{now.year-1}-12"
            else:
                last_month = f"{now.year}-{now.month-1:02d}"
            
            filtered = [e for e in filtered if e.date and e.date.startswith(last_month)]
        
        elif date_filter == "custom":
            # Custom date range
            start = self.start_date.get_date().strftime("%Y-%m-%d")
            end = self.end_date.get_date().strftime("%Y-%m-%d")
            
            # Make sure date is not None and is in proper format before comparing
            filtered = [e for e in filtered if e.date and start <= e.date <= end]
        
        # Apply category filter
        if category_filter != "all":
            # Check if category is a main category (might have subcategories)
            is_main = category_filter in self.categories_dict
            
            if is_main:
                selected_category = self.categories_dict[category_filter]
                
                # If it's a main category, include all expenses with this category or its subcategories
                if selected_category.parent_id is None:  # It's definitely a main category
                    # Get all subcategory IDs for this main category
                    subcategory_ids = [
                        cat_id for cat_id, cat in self.categories_dict.items()
                        if cat.parent_id == category_filter
                    ]
                    
                    # Include the main category and all its subcategories
                    filtered = [
                        e for e in filtered 
                        if e.category_id == category_filter or e.category_id in subcategory_ids
                    ]
                else:
                    # It's a subcategory, just match directly
                    filtered = [e for e in filtered if e.category_id == category_filter]
            else:
                # If it's not found (which shouldn't happen), just do a direct match
                filtered = [e for e in filtered if e.category_id == category_filter]
        
        # Apply type filter
        if type_filter == "expense":
            filtered = [e for e in filtered if not e.is_income]
        elif type_filter == "income":
            filtered = [e for e in filtered if e.is_income]
        
        # Apply search text
        if search_text:
            filtered = [e for e in filtered if (
                search_text in e.description.lower() or
                search_text in (self.categories_dict.get(e.category_id).name.lower() 
                               if e.category_id in self.categories_dict else "")
            )]
        
        # Update filtered expenses and refresh UI
        self.filtered_expenses = filtered
        self._show_expenses_list()
    
    def _populate_category_filters(self):
        """Populate the category filter section with available categories."""
        # Clear existing widgets
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        # Add category radio buttons
        for i, (cat_id, category) in enumerate(self.categories_dict.items()):
            # Skip subcategories to keep the list cleaner
            if category.parent_id:
                continue
                
            cat_radio = ttk.Radiobutton(
                self.category_frame, 
                text=category.name, 
                value=cat_id,
                variable=self.category_var,
                command=self._apply_filters
            )
            cat_radio.grid(row=i, column=0, sticky="w", pady=2)
    
    def show_add_expense_dialog(self):
        """Show dialog for adding a new expense."""
        dialog = tk.Toplevel(self)
        dialog.title("Add Expense")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Add padding around the form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        # Transaction type
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=5)
        
        ttk.Label(type_frame, text="Transaction Type:").pack(side="left")
        
        type_var = tk.StringVar(value="expense")
        expense_radio = ttk.Radiobutton(type_frame, text="Expense", value="expense", variable=type_var,
                                      command=lambda: self._update_category_list(category_combo, type_var.get()))
        expense_radio.pack(side="left", padx=10)
        
        income_radio = ttk.Radiobutton(type_frame, text="Income", value="income", variable=type_var,
                                     command=lambda: self._update_category_list(category_combo, type_var.get()))
        income_radio.pack(side="left", padx=10)
        
        # Amount field
        amount_frame = ttk.Frame(form_frame)
        amount_frame.pack(fill="x", pady=5)
        
        ttk.Label(amount_frame, text="Amount:").pack(side="left")
        amount_var = tk.StringVar()
        amount_entry = ttk.Entry(amount_frame, textvariable=amount_var, width=15)
        amount_entry.pack(side="left", padx=10)
        
        # Date field
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side="left")
        date_entry = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        date_entry.pack(side="left", padx=10)
        
        # Category field
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill="x", pady=5)
        
        ttk.Label(category_frame, text="Category:").pack(side="left")
        
        # Create combobox first, will populate later
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(category_frame, textvariable=category_var, width=30)
        category_combo.pack(side="left", padx=10)
        
        # Populate with appropriate categories based on initial selection
        self._update_category_list(category_combo, type_var.get())
        
        # Description field
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill="x", pady=5)
        
        ttk.Label(desc_frame, text="Description:").pack(anchor="w")
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=desc_var, width=40)
        desc_entry.pack(fill="x", pady=5)
        
        # Payment method field
        payment_frame = ttk.Frame(form_frame)
        payment_frame.pack(fill="x", pady=5)
        
        ttk.Label(payment_frame, text="Payment Method:").pack(side="left")
        payment_var = tk.StringVar()
        payment_methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "PayPal", "Other"]
        payment_combo = ttk.Combobox(payment_frame, textvariable=payment_var, values=payment_methods, width=15)
        payment_combo.pack(side="left", padx=10)
        
        # Recurring option
        recurring_frame = ttk.Frame(form_frame)
        recurring_frame.pack(fill="x", pady=5)
        
        recurring_var = tk.BooleanVar(value=False)
        recurring_check = ttk.Checkbutton(recurring_frame, text="Recurring Transaction", variable=recurring_var)
        recurring_check.pack(side="left")
        
        # Recurring details (initially hidden)
        recurring_details = ttk.Frame(form_frame)
        recurring_details.pack(fill="x", pady=5)
        recurring_details.pack_forget()  # Hide initially
        
        ttk.Label(recurring_details, text="Frequency:").pack(side="left")
        period_var = tk.StringVar(value="monthly")
        period_options = ["daily", "weekly", "monthly", "yearly"]
        period_combo = ttk.Combobox(recurring_details, textvariable=period_var, values=period_options, width=10)
        period_combo.pack(side="left", padx=10)
        
        ttk.Label(recurring_details, text="End Date:").pack(side="left", padx=(10, 0))
        end_date_entry = DateEntry(recurring_details, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        end_date_entry.pack(side="left", padx=10)
        
        # Tags field
        tags_frame = ttk.Frame(form_frame)
        tags_frame.pack(fill="x", pady=5)
        
        ttk.Label(tags_frame, text="Tags (comma separated):").pack(anchor="w")
        tags_var = tk.StringVar()
        tags_entry = ttk.Entry(tags_frame, textvariable=tags_var, width=40)
        tags_entry.pack(fill="x", pady=5)
        
        # Error message
        error_var = tk.StringVar()
        error_label = ttk.Label(form_frame, textvariable=error_var, foreground="#e74c3c")
        error_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save", style="Primary.TButton",
                           command=lambda: self._save_new_expense(
                               type_var.get(), amount_var.get(), date_entry.get_date(),
                               category_combo.get(), desc_var.get(), payment_var.get(),
                               recurring_var.get(), period_var.get(), end_date_entry.get_date(),
                               tags_var.get(), error_var, dialog
                           ))
        save_btn.pack(side="right", padx=5)
        
        # Show/hide recurring details based on checkbox
        def toggle_recurring():
            if recurring_var.get():
                recurring_details.pack(fill="x", pady=5, after=recurring_frame)
            else:
                recurring_details.pack_forget()
        
        recurring_check.config(command=toggle_recurring)
        
        # Set focus to amount field
        amount_entry.focus_set()
    
    def _update_category_list(self, combo_widget, transaction_type):
        """Update the category dropdown list based on transaction type (income/expense)."""
        # Create hierarchical category list
        categories = []
        category_to_id = {}  # Map to store the displayed name to category ID
        main_categories = {}
        
        # First, find all appropriate categories based on transaction type
        is_income = (transaction_type == "income")
        
        # Find main categories matching the transaction type
        for cat_id, cat in self.categories_dict.items():
            # Check if category matches the transaction type (income or expense)
            if not cat.parent_id and cat.is_income == is_income:
                main_categories[cat_id] = cat.name
                display_name = cat.name
                categories.append(display_name)
                category_to_id[display_name] = cat_id
        
        # Then add subcategories with parent names
        for cat_id, cat in self.categories_dict.items():
            # Make sure subcategory matches transaction type and its parent is in our main categories list
            if cat.parent_id and cat.parent_id in main_categories and cat.is_income == is_income:
                parent_name = main_categories[cat.parent_id]
                display_name = f"{parent_name} > {cat.name}"
                categories.append(display_name)
                category_to_id[display_name] = cat_id
        
        # Sort categories alphabetically
        categories.sort()
        
        # Store mapping in an attribute for later use
        self.category_to_id = category_to_id
        
        # Update the combobox values
        combo_widget['values'] = categories
        if categories:
            combo_widget.current(0)
        else:
            combo_widget.set('')  # Clear the selection if no categories available
    
    def _save_new_expense(self, type_str, amount_str, date_obj, category_str, description, 
                         payment_method, recurring, period, end_date, tags_str, error_var, dialog):
        """Save a new expense from the dialog data."""
        user_id = self.controller.current_user.user_id if self.controller.current_user else None
        
        if not user_id:
            error_var.set("You must be logged in to add expenses")
            return
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                error_var.set("Amount must be greater than zero")
                return
        except ValueError:
            error_var.set("Amount must be a valid number")
            return
        
        # Get date in ISO format
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Get category ID from the displayed name
        category_name = category_str
        if not category_name and type_str == "expense":
            error_var.set("Please select a category for the expense")
            return
        
        # Get the category ID from our mapping
        category_id = self.category_to_id.get(category_name) if category_name else None
        
        # Process tags
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Process recurring end date
        recurring_end_date = end_date.strftime("%Y-%m-%d") if recurring else None
        
        # Create expense object
        expense = Expense(
            amount=amount,
            category_id=category_id,
            date=date_str,
            description=description,
            user_id=user_id,
            payment_method=payment_method if payment_method else None,
            recurring=recurring,
            recurring_period=period if recurring else None,
            recurring_end_date=recurring_end_date,
            tags=tags,
            is_income=(type_str == "income")
        )
        
        # Save expense
        if expense.save(self.controller.data_dir):
            dialog.destroy()
            self.refresh_data()
        else:
            error_var.set("Error saving expense. Please try again.")
    
    def _show_edit_expense_dialog(self, expense):
        """Show dialog for editing an existing expense."""
        dialog = tk.Toplevel(self)
        dialog.title("Edit Expense")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Add padding around the form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        # Transaction type
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=5)
        
        ttk.Label(type_frame, text="Transaction Type:").pack(side="left")
        
        type_var = tk.StringVar(value="income" if expense.is_income else "expense")
        expense_radio = ttk.Radiobutton(type_frame, text="Expense", value="expense", variable=type_var)
        expense_radio.pack(side="left", padx=10)
        
        income_radio = ttk.Radiobutton(type_frame, text="Income", value="income", variable=type_var)
        income_radio.pack(side="left", padx=10)
        
        # Amount field
        amount_frame = ttk.Frame(form_frame)
        amount_frame.pack(fill="x", pady=5)
        
        ttk.Label(amount_frame, text="Amount:").pack(side="left")
        amount_var = tk.StringVar(value=str(expense.amount))
        amount_entry = ttk.Entry(amount_frame, textvariable=amount_var, width=15)
        amount_entry.pack(side="left", padx=10)
        
        # Date field
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill="x", pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side="left")
        date_entry = DateEntry(date_frame, width=12, background='darkblue',
                              foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        try:
            date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
            date_entry.set_date(date_obj)
        except ValueError:
            pass  # Use the default (current) date if there's an issue
        date_entry.pack(side="left", padx=10)
        
        # Category field
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill="x", pady=5)
        
        ttk.Label(category_frame, text="Category:").pack(side="left")
        
        # Create hierarchical category list
        categories = []
        category_to_id = {}  # Map to store the displayed name to category ID
        main_categories = {}
        category_to_select = None
        
        # First, find all main categories
        for cat_id, cat in self.categories_dict.items():
            if not cat.parent_id:  # Main category
                main_categories[cat_id] = cat.name
                display_name = cat.name
                categories.append(display_name)
                category_to_id[display_name] = cat_id
                
                # If this is the selected category, make note of it
                if cat_id == expense.category_id:
                    category_to_select = display_name
        
        # Then add subcategories with parent names
        for cat_id, cat in self.categories_dict.items():
            if cat.parent_id and cat.parent_id in main_categories:  # Subcategory
                parent_name = main_categories[cat.parent_id]
                display_name = f"{parent_name} > {cat.name}"
                categories.append(display_name)
                category_to_id[display_name] = cat_id
                
                # If this is the selected category, make note of it
                if cat_id == expense.category_id:
                    category_to_select = display_name
        
        # Sort categories alphabetically
        categories.sort()
        
        category_var = tk.StringVar(value=category_to_select if category_to_select else "")
        category_combo = ttk.Combobox(category_frame, textvariable=category_var, values=categories, width=30)
        category_combo.pack(side="left", padx=10)
        
        # Description field
        desc_frame = ttk.Frame(form_frame)
        desc_frame.pack(fill="x", pady=5)
        
        ttk.Label(desc_frame, text="Description:").pack(anchor="w")
        desc_var = tk.StringVar(value=expense.description)
        desc_entry = ttk.Entry(desc_frame, textvariable=desc_var, width=40)
        desc_entry.pack(fill="x", pady=5)
        
        # Payment method field
        payment_frame = ttk.Frame(form_frame)
        payment_frame.pack(fill="x", pady=5)
        
        ttk.Label(payment_frame, text="Payment Method:").pack(side="left")
        payment_var = tk.StringVar(value=expense.payment_method if expense.payment_method else "")
        payment_methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "PayPal", "Other"]
        payment_combo = ttk.Combobox(payment_frame, textvariable=payment_var, values=payment_methods, width=15)
        payment_combo.pack(side="left", padx=10)
        
        # Recurring option
        recurring_frame = ttk.Frame(form_frame)
        recurring_frame.pack(fill="x", pady=5)
        
        recurring_var = tk.BooleanVar(value=expense.recurring)
        recurring_check = ttk.Checkbutton(recurring_frame, text="Recurring Transaction", variable=recurring_var)
        recurring_check.pack(side="left")
        
        # Recurring details
        recurring_details = ttk.Frame(form_frame)
        if expense.recurring:
            recurring_details.pack(fill="x", pady=5)
        else:
            recurring_details.pack_forget()  # Hide initially
        
        ttk.Label(recurring_details, text="Frequency:").pack(side="left")
        period_var = tk.StringVar(value=expense.recurring_period if expense.recurring_period else "monthly")
        period_options = ["daily", "weekly", "monthly", "yearly"]
        period_combo = ttk.Combobox(recurring_details, textvariable=period_var, values=period_options, width=10)
        period_combo.pack(side="left", padx=10)
        
        ttk.Label(recurring_details, text="End Date:").pack(side="left", padx=(10, 0))
        end_date_entry = DateEntry(recurring_details, width=12, background='darkblue',
                                  foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        if expense.recurring_end_date:
            try:
                end_date_obj = datetime.strptime(expense.recurring_end_date, "%Y-%m-%d")
                end_date_entry.set_date(end_date_obj)
            except ValueError:
                pass  # Use the default date if there's an issue
        end_date_entry.pack(side="left", padx=10)
        
        # Tags field
        tags_frame = ttk.Frame(form_frame)
        tags_frame.pack(fill="x", pady=5)
        
        ttk.Label(tags_frame, text="Tags (comma separated):").pack(anchor="w")
        tags_var = tk.StringVar(value=", ".join(expense.tags) if expense.tags else "")
        tags_entry = ttk.Entry(tags_frame, textvariable=tags_var, width=40)
        tags_entry.pack(fill="x", pady=5)
        
        # Error message
        error_var = tk.StringVar()
        error_label = ttk.Label(form_frame, textvariable=error_var, foreground="#e74c3c")
        error_label.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save Changes", style="Primary.TButton",
                            command=lambda: self._update_expense(
                                expense, type_var.get(), amount_var.get(), date_entry.get_date(),
                                category_combo.get(), desc_var.get(), payment_var.get(),
                                recurring_var.get(), period_var.get(), end_date_entry.get_date(),
                                tags_var.get(), error_var, dialog
                            ))
        save_btn.pack(side="right", padx=5)
        
        # Show/hide recurring details based on checkbox
        def toggle_recurring():
            if recurring_var.get():
                recurring_details.pack(fill="x", pady=5, after=recurring_frame)
            else:
                recurring_details.pack_forget()
        
        recurring_check.config(command=toggle_recurring)
    
    def _update_expense(self, expense, type_str, amount_str, date_obj, category_str, description, 
                       payment_method, recurring, period, end_date, tags_str, error_var, dialog):
        """Update an existing expense with new data."""
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                error_var.set("Amount must be greater than zero")
                return
        except ValueError:
            error_var.set("Amount must be a valid number")
            return
        
        # Get date in ISO format
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Get category ID from the displayed name
        category_name = category_str
        if not category_name:
            error_var.set("Please select a category")
            return
        
        # Get the category ID from our mapping
        category_id = self.category_to_id.get(category_name) if category_name else None
        
        # Process tags
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Process recurring end date
        recurring_end_date = end_date.strftime("%Y-%m-%d") if recurring else None
        
        # Update expense object
        expense.amount = amount
        expense.category_id = category_id
        expense.date = date_str
        expense.description = description
        expense.payment_method = payment_method if payment_method else None
        expense.recurring = recurring
        expense.recurring_period = period if recurring else None
        expense.recurring_end_date = recurring_end_date
        expense.tags = tags
        expense.is_income = (type_str == "income")
        
        # Save expense
        if expense.save(self.controller.data_dir):
            dialog.destroy()
            self.refresh_data()
        else:
            error_var.set("Error updating expense. Please try again.")
    
    def _confirm_delete_expense(self, expense):
        """Confirm and delete an expense."""
        if self.ask_yes_no("Confirm Delete", 
                          f"Are you sure you want to delete this {('income' if expense.is_income else 'expense')}?"):
            # Get the file path
            user_id = self.controller.current_user.user_id
            expense_file = os.path.join(self.controller.data_dir, "expenses", user_id, f"{expense.expense_id}.json")
            
            try:
                if os.path.exists(expense_file):
                    os.remove(expense_file)
                
                self.refresh_data()
                self.show_message("Success", "Expense deleted successfully", "info")
            except Exception as e:
                self.show_message("Error", f"Error deleting expense: {str(e)}", "error")
    
    def refresh_data(self):
        """Refresh the expense data and view."""
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
            categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.categories_dict = {cat.category_id: cat for cat in categories}
            
            # Ensure "Income" category has is_income=True
            for cat_id, cat in self.categories_dict.items():
                if cat.name == "Income" or cat.name in ["Salary", "Bonus", "Interest", "Dividends", "Freelance", "Rental"]:
                    cat.is_income = True
                    cat.save(self.controller.data_dir)
            
            # Populate category filters
            self._populate_category_filters()
            
            # Apply current filters
            self._apply_filters()
        else:
            self.expenses = []
            self.filtered_expenses = []
            self.categories_dict = {}
            
            # Update UI
            self._show_expenses_list()
    
    def on_show_frame(self):
        """Called when the frame is shown."""
        # Update user info
        if self.controller.current_user:
            self.user_var.set(f"Welcome, {self.controller.current_user.username}")
        else:
            self.user_var.set("Welcome, User")
        
        # Refresh expenses data
        self.refresh_data()

    def _export_to_csv(self):
        """Export expenses to a CSV file."""
        try:
            if not self.controller.current_user:
                self.show_message("Error", "Please log in to export expenses", "error")
                return
                
            if not self.filtered_expenses:
                self.show_message("No Data", "There are no expenses to export", "info")
                return
                
            # Ask user to select a destination file
            file_path = filedialog.asksaveasfilename(
                title="Export Expenses",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return  # User cancelled
            
            # Use the centralized export function
            success, result, filename = export_expenses_to_csv(file_path, self.filtered_expenses, self.categories_dict)
            
            if success:
                self.show_message(
                    "Export Complete", 
                    f"Successfully exported {result} transactions to {filename}", 
                    "info"
                )
            else:
                self.show_message("Error", f"Failed to export file: {result}", "error")
                
        except Exception as e:
            self.show_message("Error", f"Failed to export file: {str(e)}", "error")

    def show_message(self, title, message, message_type="info"):
        """Show a message dialog to the user."""
        icon = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }.get(message_type, "ℹ️")
        
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog on parent
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_rooty() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Icon and message
        message_frame = ttk.Frame(frame)
        message_frame.pack(fill="both", expand=True)
        
        icon_label = ttk.Label(message_frame, text=icon, font=("Helvetica", 24))
        icon_label.pack(side="left", padx=(0, 10))
        
        msg_label = ttk.Label(message_frame, text=message, wraplength=250)
        msg_label.pack(side="left", fill="both", expand=True)
        
        # OK button
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ok_button = ttk.Button(button_frame, text="OK", command=dialog.destroy)
        ok_button.pack(side="right")
        
        # Set focus to OK button
        ok_button.focus_set()
        
        # Bind Enter key to close dialog
        dialog.bind("<Return>", lambda event: dialog.destroy())
