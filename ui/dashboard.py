"""
Dashboard UI components for the expense tracking system.
This module provides UI components for the main dashboard.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .base import BaseFrame, ScrollableFrame, Tooltip
from models.expense import Expense
from models.category import Category
from utils.analysis import get_monthly_summary, compare_time_periods, detect_spending_anomalies, export_expenses_to_csv
from utils.visualization import create_expense_pie_chart, create_monthly_trend_chart, figure_to_image


class DashboardFrame(BaseFrame):
    """Main dashboard for the expense tracking system."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new DashboardFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.expenses = []
        self.categories_dict = {}
        self.plot_frame = None
        self.chart_canvas = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dashboard widgets."""
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
        
        # Create sidebar for navigation
        self._create_sidebar(content)
        
        # Create main panel
        self.main_panel = ttk.Frame(content)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)
        
        # Show overview panel by default
        self._show_overview_panel()
    
    def _create_navbar(self, parent):
        """Create the top navigation bar."""
        navbar = ttk.Frame(parent, style="Card.TFrame", padding=10)
        navbar.grid(row=0, column=0, sticky="ew")
        
        # App title
        title_label = ttk.Label(navbar, text="Expense Tracker", style="Title.TLabel")
        title_label.pack(side="left", padx=10)
        
        # User info and settings
        user_frame = ttk.Frame(navbar)
        user_frame.pack(side="right", padx=10)
        
        self.user_var = tk.StringVar(value="Welcome, User")
        user_label = ttk.Label(user_frame, textvariable=self.user_var)
        user_label.pack(side="left", padx=5)
        
        profile_button = ttk.Button(user_frame, text="Profile", width=8,
                                  command=self._handle_profile)
        profile_button.pack(side="left", padx=5)
        
        logout_button = ttk.Button(user_frame, text="Logout", width=8,
                                 command=self._handle_logout)
        logout_button.pack(side="left", padx=5)
    
    def _create_sidebar(self, parent):
        """Create the sidebar for navigation."""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        
        # Add section labels and buttons
        overview_btn = ttk.Button(sidebar, text="Dashboard", width=20, 
                                command=self._show_overview_panel)
        overview_btn.pack(pady=5, fill="x")
        
        expenses_btn = ttk.Button(sidebar, text="Expenses", width=20,
                                command=lambda: self.controller.show_frame("ExpensesFrame"))
        expenses_btn.pack(pady=5, fill="x")
        
        categories_btn = ttk.Button(sidebar, text="Categories", width=20,
                                  command=lambda: self.controller.show_frame("CategoriesFrame"))
        categories_btn.pack(pady=5, fill="x")
        
        reports_btn = ttk.Button(sidebar, text="Reports", width=20,
                               command=lambda: self.controller.show_frame("ReportsFrame"))
        reports_btn.pack(pady=5, fill="x")
        
        budget_btn = ttk.Button(sidebar, text="Budgets", width=20,
                              command=lambda: self.controller.show_frame("BudgetsFrame"))
        budget_btn.pack(pady=5, fill="x")
        
        export_btn = ttk.Button(sidebar, text="Export Data", width=20,
                                    command=self._export_data)
        export_btn.pack(pady=5, fill="x")
        
        # Add spacer
        ttk.Separator(sidebar, orient="horizontal").pack(pady=10, fill="x")
        
        # Quick add expense button
        add_expense_btn = ttk.Button(sidebar, text="Add Expense", width=20,
                                   command=self._quick_add_expense, style="Primary.TButton")
        add_expense_btn.pack(pady=5, fill="x")
    
    def _show_overview_panel(self):
        """Show the overview panel in the main area."""
        # Clear the main panel
        for widget in self.main_panel.winfo_children():
            widget.destroy()
        
        # Create scrollable container
        scrollable = ScrollableFrame(self.main_panel)
        scrollable.pack(side="top", fill="both", expand=True)
        container = scrollable.scrollable_frame
        
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Add header with date
        header_frame = ttk.Frame(container)
        header_frame.pack(pady=10, fill="x")
        
        date_label = ttk.Label(header_frame, text=f"Overview • {current_date}", style="Title.TLabel")
        date_label.pack(side="left", padx=20)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", width=10,
                               command=self._refresh_dashboard)
        refresh_btn.pack(side="right", padx=20)
        
        # Get user's expenses and categories
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
            categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.categories_dict = {cat.category_id: cat for cat in categories}
            
            # Get monthly summary
            summary = get_monthly_summary(self.expenses, self.categories_dict)
            
            # Create summary cards row
            cards_frame = ttk.Frame(container)
            cards_frame.pack(pady=10, fill="x", padx=20)
            
            # Configure grid for cards
            for i in range(3):
                cards_frame.grid_columnconfigure(i, weight=1)
            
            # Income card
            income_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
            income_card.grid(row=0, column=0, padx=10, sticky="ew")
            
            income_title = ttk.Label(income_card, text="Monthly Income", font=("Helvetica", 12))
            income_title.pack(anchor="w")
            
            income_amount = ttk.Label(income_card, text=f"${summary['total_income']:.2f}", 
                                    font=("Helvetica", 20, "bold"), foreground="#2ecc71")
            income_amount.pack(pady=5)
            
            # Expenses card
            expense_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
            expense_card.grid(row=0, column=1, padx=10, sticky="ew")
            
            expense_title = ttk.Label(expense_card, text="Monthly Expenses", font=("Helvetica", 12))
            expense_title.pack(anchor="w")
            
            expense_amount = ttk.Label(expense_card, text=f"${summary['total_expenses']:.2f}", 
                                     font=("Helvetica", 20, "bold"), foreground="#e74c3c")
            expense_amount.pack(pady=5)
            
            # Balance card
            balance_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
            balance_card.grid(row=0, column=2, padx=10, sticky="ew")
            
            balance_title = ttk.Label(balance_card, text="Net Balance", font=("Helvetica", 12))
            balance_title.pack(anchor="w")
            
            # Determine color based on net value
            balance_color = "#2ecc71" if summary['net'] >= 0 else "#e74c3c"
            
            balance_amount = ttk.Label(balance_card, text=f"${summary['net']:.2f}", 
                                     font=("Helvetica", 20, "bold"), foreground=balance_color)
            balance_amount.pack(pady=5)
            
            # Add charts section
            charts_frame = ttk.Frame(container)
            charts_frame.pack(pady=20, fill="x", padx=20)
            
            charts_title = ttk.Label(charts_frame, text="Expense Analysis", style="Subtitle.TLabel")
            charts_title.pack(anchor="w", pady=(0, 10))
            
            # Create plot frame
            plot_frame = ttk.Frame(charts_frame, style="Card.TFrame", padding=5)
            plot_frame.pack(fill="both", expand=True)
            
            # Create the pie chart
            self._show_category_pie_chart(plot_frame)
            
            # Create trend chart frame
            trend_frame = ttk.Frame(container)
            trend_frame.pack(pady=(0, 20), fill="x", padx=20)
            
            trend_title = ttk.Label(trend_frame, text="Monthly Trends", style="Subtitle.TLabel")
            trend_title.pack(anchor="w", pady=(0, 10))
            
            # Create trend plot frame
            trend_plot_frame = ttk.Frame(trend_frame, style="Card.TFrame", padding=5)
            trend_plot_frame.pack(fill="both", expand=True)
            
            # Create the trend chart
            self._show_monthly_trend_chart(trend_plot_frame)
            
            # Create anomalies section
            anomalies = detect_spending_anomalies(self.expenses, self.categories_dict)
            if anomalies:
                anomaly_frame = ttk.Frame(container)
                anomaly_frame.pack(pady=(0, 20), fill="x", padx=20)
                
                anomaly_title = ttk.Label(anomaly_frame, text="Spending Anomalies", style="Subtitle.TLabel")
                anomaly_title.pack(anchor="w", pady=(0, 10))
                
                anomaly_list = ttk.Frame(anomaly_frame, style="Card.TFrame", padding=15)
                anomaly_list.pack(fill="x")
                
                # Show up to 3 anomalies
                for i, anomaly in enumerate(anomalies[:3]):
                    item_frame = ttk.Frame(anomaly_list)
                    item_frame.pack(fill="x", pady=5)
                    
                    if anomaly['anomaly_type'] == 'large_transaction':
                        text = f"Unusually large expense of ${anomaly['amount']:.2f} in " \
                               f"{anomaly['category']} on {anomaly['date']}."
                        icon_text = "⚠️"
                    else:
                        text = f"High transaction frequency on {anomaly['date']} " \
                               f"with {anomaly['count']} transactions."
                        icon_text = "📊"
                    
                    icon = ttk.Label(item_frame, text=icon_text, font=("Helvetica", 14))
                    icon.pack(side="left", padx=(0, 10))
                    
                    label = ttk.Label(item_frame, text=text, wraplength=600)
                    label.pack(side="left", fill="x", expand=True)
            
            # Create recent transactions section
            recent_frame = ttk.Frame(container)
            recent_frame.pack(pady=(0, 20), fill="x", padx=20)
            
            recent_header = ttk.Frame(recent_frame)
            recent_header.pack(fill="x")
            
            recent_title = ttk.Label(recent_header, text="Recent Transactions", style="Subtitle.TLabel")
            recent_title.pack(side="left")
            
            view_all_btn = ttk.Button(recent_header, text="View All", width=10,
                                    command=lambda: self.controller.show_frame("ExpensesFrame"))
            view_all_btn.pack(side="right")
            
            # Recent transactions list
            recent_list = ttk.Frame(recent_frame, style="Card.TFrame", padding=15)
            recent_list.pack(fill="x", pady=(10, 0))
            
            # Headers
            headers_frame = ttk.Frame(recent_list)
            headers_frame.pack(fill="x", pady=(0, 5))
            
            date_header = ttk.Label(headers_frame, text="Date", width=12, font=("Helvetica", 10, "bold"))
            date_header.pack(side="left", padx=5)
            
            description_header = ttk.Label(headers_frame, text="Description", width=25, font=("Helvetica", 10, "bold"))
            description_header.pack(side="left", padx=5)
            
            category_header = ttk.Label(headers_frame, text="Category", width=15, font=("Helvetica", 10, "bold"))
            category_header.pack(side="left", padx=5)
            
            amount_header = ttk.Label(headers_frame, text="Amount", width=10, font=("Helvetica", 10, "bold"))
            amount_header.pack(side="left", padx=5)
            
            ttk.Separator(recent_list, orient="horizontal").pack(fill="x", pady=5)
            
            # List recent transactions (up to 5)
            recent_expenses = sorted(self.expenses, key=lambda x: x.date, reverse=True)[:5]
            
            if recent_expenses:
                for expense in recent_expenses:
                    item_frame = ttk.Frame(recent_list)
                    item_frame.pack(fill="x", pady=2)
                    
                    date_label = ttk.Label(item_frame, text=expense.date, width=12)
                    date_label.pack(side="left", padx=5)
                    
                    desc_label = ttk.Label(item_frame, text=expense.description[:30], width=25)
                    desc_label.pack(side="left", padx=5)
                    
                    # Get category name
                    category_name = "Unknown"
                    if expense.category_id in self.categories_dict:
                        category_name = self.categories_dict[expense.category_id].name
                    
                    cat_label = ttk.Label(item_frame, text=category_name[:15], width=15)
                    cat_label.pack(side="left", padx=5)
                    
                    # Format amount based on income/expense
                    amount = expense.amount
                    amount_text = f"${amount:.2f}"
                    amount_color = "#2ecc71" if expense.is_income else "#e74c3c"
                    
                    amount_label = ttk.Label(item_frame, text=amount_text, width=10, foreground=amount_color)
                    amount_label.pack(side="left", padx=5)
            else:
                no_data_label = ttk.Label(recent_list, text="No recent transactions")
                no_data_label.pack(pady=10)
        else:
            # User not logged in
            error_label = ttk.Label(container, text="You must be logged in to view the dashboard", 
                                  foreground="#e74c3c", font=("Helvetica", 14))
            error_label.pack(pady=50)
            
            login_btn = ttk.Button(container, text="Go to Login", 
                                 command=lambda: self.controller.show_frame("LoginFrame"))
            login_btn.pack()
    
    def _show_category_pie_chart(self, parent):
        """Create and show the category distribution pie chart."""
        if not self.expenses:
            # No data, show message
            no_data_label = ttk.Label(parent, text="No expense data available for chart")
            no_data_label.pack(pady=50)
            return
        
        # Create the chart
        fig = create_expense_pie_chart(self.expenses, self.categories_dict)
        
        # Display the chart in the frame
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.chart_canvas = canvas
    
    def _show_monthly_trend_chart(self, parent):
        """Create and show the monthly trend chart."""
        if not self.expenses:
            # No data, show message
            no_data_label = ttk.Label(parent, text="No expense data available for chart")
            no_data_label.pack(pady=50)
            return
        
        # Create the chart
        fig = create_monthly_trend_chart(self.expenses, self.categories_dict)
        
        # Display the chart in the frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _handle_profile(self):
        """Handle clicking the profile button."""
        self.controller.show_frame("ProfileFrame")
    
    def _handle_logout(self):
        """Handle clicking the logout button."""
        if self.ask_yes_no("Confirm Logout", "Are you sure you want to log out?"):
            self.controller.current_user = None
            self.controller.show_frame("LoginFrame")
    
    def _quick_add_expense(self):
        """Show dialog for quickly adding an expense."""
        self.controller.show_frame("ExpensesFrame")
        if hasattr(self.controller.frames["ExpensesFrame"], "show_add_expense_dialog"):
            self.controller.frames["ExpensesFrame"].show_add_expense_dialog()
    
    def _refresh_dashboard(self):
        """Refresh the dashboard data and view."""
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
            categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.categories_dict = {cat.category_id: cat for cat in categories}
        
        self._show_overview_panel()
    
    def _export_data(self):
        """Export expense data to CSV file."""
        # Ensure user is logged in
        if not self.controller.current_user:
            self.show_message("Error", "Please log in to export expense data.", "error")
            return
        
        # Get user's expenses
        user_id = self.controller.current_user.user_id
        expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
        categories = Category.get_all_categories(user_id, self.controller.data_dir)
        categories_dict = {cat.category_id: cat for cat in categories}
        
        if not expenses:
            self.show_message("No Data", "There are no expenses to export.", "info")
            return
        
        # Ask user for file location
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Export Expenses",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
            
        # Use the centralized export function
        success, result, filename = export_expenses_to_csv(file_path, expenses, categories_dict)
        
        if success:
            self.show_message(
                "Export Complete", 
                f"Successfully exported {result} transactions to {filename}", 
                "info"
            )
        else:
            self.show_message("Error", f"Failed to export file: {result}", "error")
    
    def on_show_frame(self):
        """Called when the frame is shown."""
        # Update user info
        if self.controller.current_user:
            self.user_var.set(f"Welcome, {self.controller.current_user.username}")
        else:
            self.user_var.set("Welcome, User")
        
        # Refresh dashboard
        self._refresh_dashboard()
