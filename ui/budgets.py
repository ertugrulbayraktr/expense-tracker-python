"""
Budget management UI components for the expense tracking system.
This module provides UI components for creating and managing expense budgets.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import calendar
from .base import BaseFrame, ScrollableFrame, Tooltip
from models.category import Category
from models.expense import Expense


class BudgetsFrame(BaseFrame):
    """Main frame for managing expense budgets."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new BudgetsFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize variables
        self.categories = []
        self.category_dict = {}
        self.expenses = []
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the budget management widgets."""
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
        
        # Show budgets list by default
        self._show_budgets_list()
    
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
        
        title_label = ttk.Label(title_frame, text="Budgets", style="Title.TLabel")
        title_label.pack(side="left", padx=5)
        
        # User info
        user_frame = ttk.Frame(navbar)
        user_frame.pack(side="right", padx=10)
        
        self.user_var = tk.StringVar(value="Welcome, User")
        user_label = ttk.Label(user_frame, textvariable=self.user_var)
        user_label.pack(side="left", padx=5)
    
    def _create_sidebar(self, parent):
        """Create the sidebar with options."""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        
        # Month selection
        month_frame = ttk.LabelFrame(sidebar, text="Month")
        month_frame.pack(fill="x", pady=10)
        
        month_names = calendar.month_name[1:]
        self.month_var = tk.StringVar(value=calendar.month_name[self.current_month])
        month_combo = ttk.Combobox(month_frame, textvariable=self.month_var, values=month_names, state="readonly")
        month_combo.pack(fill="x", padx=5, pady=5)
        month_combo.bind("<<ComboboxSelected>>", lambda e: self._update_month())
        
        # Year selection
        year_frame = ttk.Frame(month_frame)
        year_frame.pack(fill="x", padx=5, pady=5)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        prev_year_btn = ttk.Button(year_frame, text="◀", width=2, 
                                  command=self._previous_year)
        prev_year_btn.pack(side="left")
        
        year_label = ttk.Label(year_frame, textvariable=self.year_var, width=6)
        year_label.pack(side="left", padx=5)
        
        next_year_btn = ttk.Button(year_frame, text="▶", width=2,
                                  command=self._next_year)
        next_year_btn.pack(side="left")
        
        # Filter options
        filter_frame = ttk.LabelFrame(sidebar, text="View Options")
        filter_frame.pack(fill="x", pady=10)
        
        self.view_var = tk.StringVar(value="active")
        
        all_radio = ttk.Radiobutton(filter_frame, text="All Categories", value="all", 
                                   variable=self.view_var, command=self._refresh_view)
        all_radio.pack(anchor="w", padx=5, pady=2)
        
        active_radio = ttk.Radiobutton(filter_frame, text="Active Budgets Only", value="active", 
                                      variable=self.view_var, command=self._refresh_view)
        active_radio.pack(anchor="w", padx=5, pady=2)
        
        # Add budget button
        add_btn = ttk.Button(sidebar, text="Set Budget", style="Primary.TButton",
                           command=self._show_set_budget_dialog)
        add_btn.pack(pady=10, fill="x")
    
    def _show_budgets_list(self):
        """Show the budget list with progress in the main panel."""
        # Clear the main panel
        for widget in self.main_panel.winfo_children():
            widget.destroy()
        
        # Create scrollable container
        scrollable = ScrollableFrame(self.main_panel)
        scrollable.pack(side="top", fill="both", expand=True)
        container = scrollable.scrollable_frame
        
        # Add header with title
        header_frame = ttk.Frame(container)
        header_frame.pack(pady=10, fill="x", padx=20)
        
        # Get month name and year
        month_name = calendar.month_name[self.current_month]
        
        title_label = ttk.Label(header_frame, text=f"Budget Management - {month_name} {self.current_year}", 
                              style="Title.TLabel")
        title_label.pack(side="left")
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", width=10,
                               command=self.refresh_data)
        refresh_btn.pack(side="right")
        
        # Add budget summary
        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        summary_frame.pack(pady=10, fill="x", padx=20)
        
        # Calculate total budget and spending
        total_budget = sum(cat.budget for cat in self.categories if hasattr(cat, 'budget') and cat.budget > 0)
        total_spending = 0
        
        # Filter expenses for current month
        current_month_str = f"{self.current_year}-{self.current_month:02d}"
        month_expenses = [e for e in self.expenses if e.date.startswith(current_month_str) and not e.is_income]
        
        for expense in month_expenses:
            total_spending += expense.amount
        
        # Budget progress
        progress_frame = ttk.Frame(summary_frame)
        progress_frame.pack(fill="x", pady=10)
        
        ttk.Label(progress_frame, text="Total Budget:", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(progress_frame, text=f"${total_budget:.2f}", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, sticky="w")
        
        ttk.Label(progress_frame, text="Total Spending:", font=("Helvetica", 12, "bold")).grid(row=1, column=0, sticky="w")
        ttk.Label(progress_frame, text=f"${total_spending:.2f}", font=("Helvetica", 12)).grid(row=1, column=1, padx=10, sticky="w")
        
        remaining = total_budget - total_spending
        remaining_color = "#2ecc71" if remaining >= 0 else "#e74c3c"
        
        ttk.Label(progress_frame, text="Remaining:", font=("Helvetica", 12, "bold")).grid(row=2, column=0, sticky="w")
        ttk.Label(progress_frame, text=f"${remaining:.2f}", 
                font=("Helvetica", 12), foreground=remaining_color).grid(row=2, column=1, padx=10, sticky="w")
        
        # Create visual progress bar
        progress_percent = min(100, (total_spending / total_budget * 100)) if total_budget > 0 else 0
        
        progress_bar_frame = ttk.Frame(summary_frame)
        progress_bar_frame.pack(fill="x", pady=10)
        
        ttk.Label(progress_bar_frame, text="Budget Usage:").pack(anchor="w")
        
        bar_container = ttk.Frame(progress_bar_frame, height=20, relief="solid", borderwidth=1)
        bar_container.pack(fill="x", pady=5)
        
        # Determine color based on percentage
        if progress_percent < 75:
            bar_color = "#2ecc71"  # Green
        elif progress_percent < 90:
            bar_color = "#f39c12"  # Orange
        else:
            bar_color = "#e74c3c"  # Red
        
        # Create progress bar
        bar_width = int((progress_percent / 100) * bar_container.winfo_reqwidth())
        bar = tk.Frame(bar_container, width=bar_width, height=20, background=bar_color)
        bar.place(x=0, y=0)
        
        # Add percentage text
        percent_label = ttk.Label(bar_container, text=f"{progress_percent:.1f}%", 
                                font=("Helvetica", 10, "bold"))
        percent_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create category budgets table
        table_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        table_frame.pack(pady=20, fill="both", expand=True, padx=20)
        
        table_title = ttk.Label(table_frame, text="Category Budgets", font=("Helvetica", 12, "bold"))
        table_title.pack(anchor="w", pady=(0, 10))
        
        # Create table
        table = ttk.Frame(table_frame)
        table.pack(fill="both", expand=True)
        
        # Configure columns
        table.columnconfigure(0, weight=3)  # Category
        table.columnconfigure(1, weight=2)  # Budget
        table.columnconfigure(2, weight=2)  # Spent
        table.columnconfigure(3, weight=2)  # Remaining
        table.columnconfigure(4, weight=1)  # Actions
        
        # Headers
        ttk.Label(table, text="Category", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Budget", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Spent", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Remaining", font=("Helvetica", 10, "bold")).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Actions", font=("Helvetica", 10, "bold")).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        
        ttk.Separator(table, orient="horizontal").grid(row=1, column=0, columnspan=5, sticky="ew", pady=5)
        
        # Filter categories based on view option
        filtered_categories = self.categories
        if self.view_var.get() == "active":
            filtered_categories = [cat for cat in self.categories if hasattr(cat, 'budget') and cat.budget > 0]
        
        # Calculate spending by category
        category_spending = {}
        for expense in month_expenses:
            if expense.category_id not in category_spending:
                category_spending[expense.category_id] = 0
            category_spending[expense.category_id] += expense.amount
        
        # Display categories
        if filtered_categories:
            for i, category in enumerate(filtered_categories):
                # Get category full path if it's a subcategory
                category_name = category.name
                if category.parent_id and category.parent_id in self.category_dict:
                    parent = self.category_dict[category.parent_id]
                    category_name = f"{parent.name} > {category.name}"
                
                # Get budget and spending
                budget = category.budget if hasattr(category, 'budget') else 0
                spent = category_spending.get(category.category_id, 0)
                remaining = budget - spent
                
                # Set colors
                spent_color = "#000000"  # Default
                remaining_color = "#2ecc71" if remaining >= 0 else "#e74c3c"
                
                # Display in table
                ttk.Label(table, text=category_name).grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(table, text=f"${budget:.2f}").grid(row=i+2, column=1, sticky="w", padx=5, pady=2)
                ttk.Label(table, text=f"${spent:.2f}", foreground=spent_color).grid(row=i+2, column=2, sticky="w", padx=5, pady=2)
                ttk.Label(table, text=f"${remaining:.2f}", foreground=remaining_color).grid(row=i+2, column=3, sticky="w", padx=5, pady=2)
                
                # Actions
                actions_frame = ttk.Frame(table)
                actions_frame.grid(row=i+2, column=4, sticky="w", padx=5, pady=2)
                
                edit_btn = ttk.Button(actions_frame, text="Edit", width=5,
                                    command=lambda c=category: self._show_edit_budget_dialog(c))
                edit_btn.pack(side="left", padx=2)
                
                # Add separator between rows
                if i < len(filtered_categories) - 1:
                    ttk.Separator(table, orient="horizontal").grid(row=i+3, column=0, columnspan=5, sticky="ew", pady=2)
        else:
            no_data_label = ttk.Label(table, text="No budget data found. Click 'Set Budget' to add budgets.",
                                    font=("Helvetica", 12))
            no_data_label.grid(row=2, column=0, columnspan=5, pady=20)
    
    def _update_month(self):
        """Update the selected month and refresh the view."""
        month_name = self.month_var.get()
        for i, name in enumerate(calendar.month_name):
            if name == month_name:
                self.current_month = i
                break
        
        self._refresh_view()
    
    def _previous_year(self):
        """Move to the previous year."""
        self.current_year -= 1
        self.year_var.set(str(self.current_year))
        self._refresh_view()
    
    def _next_year(self):
        """Move to the next year."""
        self.current_year += 1
        self.year_var.set(str(self.current_year))
        self._refresh_view()
    
    def _refresh_view(self):
        """Refresh the current view."""
        self._show_budgets_list()
    
    def _show_set_budget_dialog(self):
        """Show dialog for setting a category budget."""
        # Simplified placeholder implementation
        self.show_message("Coming Soon", "Budget management will be available in a future update", "info")
    
    def _show_edit_budget_dialog(self, category):
        """Show dialog for editing a category budget."""
        # Simplified placeholder implementation
        self.show_message("Coming Soon", "Budget management will be available in a future update", "info")
    
    def refresh_data(self):
        """Refresh the category and expense data and view."""
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.category_dict = {cat.category_id: cat for cat in self.categories}
            self.expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
            
            # Refresh view
            self._refresh_view()
        else:
            self.categories = []
            self.category_dict = {}
            self.expenses = []
            
            # Show login message
            for widget in self.main_panel.winfo_children():
                widget.destroy()
            
            container = ttk.Frame(self.main_panel)
            container.pack(fill="both", expand=True)
            
            message = ttk.Label(container, text="Please log in to manage budgets", 
                              font=("Helvetica", 14))
            message.pack(pady=50)
            
            login_btn = ttk.Button(container, text="Go to Login", 
                                 command=lambda: self.controller.show_frame("LoginFrame"))
            login_btn.pack()
    
    def on_show_frame(self):
        """Called when the frame is shown."""
        # Update user info
        if self.controller.current_user:
            self.user_var.set(f"Welcome, {self.controller.current_user.username}")
        else:
            self.user_var.set("Welcome, User")
        
        # Refresh data
        self.refresh_data()
