"""
Reports UI components for the expense tracking system.
This module provides UI components for generating and viewing expense reports.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .base import BaseFrame, ScrollableFrame
from models.expense import Expense
from models.category import Category
from utils.analysis import get_monthly_summary, compare_time_periods
from utils.visualization import (
    create_expense_pie_chart, create_monthly_trend_chart,
    create_category_comparison_chart, create_spending_heatmap,
    create_budget_progress_chart
)


class ReportsFrame(BaseFrame):
    """Main frame for expense reports and analysis."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new ReportsFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize variables
        self.expenses = []
        self.categories_dict = {}
        self.current_report = "monthly_summary"
        self.chart_canvas = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the reports widgets."""
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
        
        # Show default report
        self._show_monthly_summary()
    
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
        
        title_label = ttk.Label(title_frame, text="Reports", style="Title.TLabel")
        title_label.pack(side="left", padx=5)
        
        # User info
        user_frame = ttk.Frame(navbar)
        user_frame.pack(side="right", padx=10)
        
        self.user_var = tk.StringVar(value="Welcome, User")
        user_label = ttk.Label(user_frame, textvariable=self.user_var)
        user_label.pack(side="left", padx=5)
    
    def _create_sidebar(self, parent):
        """Create the sidebar with report options."""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        
        # Report options
        reports_label = ttk.Label(sidebar, text="Report Types", font=("Helvetica", 12, "bold"))
        reports_label.pack(anchor="w", pady=(0, 10))
        
        # Monthly summary report
        monthly_btn = ttk.Button(sidebar, text="Monthly Summary", width=20,
                               command=self._show_monthly_summary)
        monthly_btn.pack(pady=5, fill="x")
        
        # Add refresh button
        refresh_btn = ttk.Button(sidebar, text="Refresh Data", width=20,
                              command=self.refresh_data)
        refresh_btn.pack(pady=(20, 5), fill="x")
    
    def _show_monthly_summary(self):
        """Show the monthly summary report."""
        # Clear the main panel
        for widget in self.main_panel.winfo_children():
            widget.destroy()
        
        self.current_report = "monthly_summary"
        
        # Create scrollable container
        scrollable = ScrollableFrame(self.main_panel)
        scrollable.pack(side="top", fill="both", expand=True)
        container = scrollable.scrollable_frame
        
        # Add header
        header_frame = ttk.Frame(container)
        header_frame.pack(pady=10, fill="x", padx=20)
        
        title_label = ttk.Label(header_frame, text="Monthly Summary Report", style="Title.TLabel")
        title_label.pack(side="left")
        
        # Get current month and year
        current_date = datetime.now()
        month_name = current_date.strftime("%B %Y")
        
        month_label = ttk.Label(header_frame, text=month_name, font=("Helvetica", 12))
        month_label.pack(side="left", padx=10)
        
        refresh_btn = ttk.Button(header_frame, text="Refresh", width=10,
                               command=self.refresh_data)
        refresh_btn.pack(side="right")
        
        # Create report content
        if not self.expenses:
            # No data available
            no_data_label = ttk.Label(container, text="No expense data available for report",
                                    font=("Helvetica", 12))
            no_data_label.pack(pady=50)
            return
        
        # Get monthly summary data
        summary = get_monthly_summary(self.expenses, self.categories_dict)
        
        # Create summary cards
        cards_frame = ttk.Frame(container)
        cards_frame.pack(pady=10, fill="x", padx=20)
        
        # Configure grid for cards
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Income card
        income_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
        income_card.grid(row=0, column=0, padx=10, sticky="ew")
        
        income_title = ttk.Label(income_card, text="Total Income", font=("Helvetica", 12))
        income_title.pack(anchor="w")
        
        income_amount = ttk.Label(income_card, text=f"${summary['total_income']:.2f}", 
                                font=("Helvetica", 20, "bold"), foreground="#2ecc71")
        income_amount.pack(pady=5)
        
        # Expenses card
        expense_card = ttk.Frame(cards_frame, style="Card.TFrame", padding=15)
        expense_card.grid(row=0, column=1, padx=10, sticky="ew")
        
        expense_title = ttk.Label(expense_card, text="Total Expenses", font=("Helvetica", 12))
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
        
        # Create pie chart for category distribution
        chart_frame = ttk.Frame(container, style="Card.TFrame", padding=10)
        chart_frame.pack(pady=20, fill="both", expand=True, padx=20)
        
        chart_title = ttk.Label(chart_frame, text="Expense Distribution by Category", 
                              font=("Helvetica", 12, "bold"))
        chart_title.pack(anchor="w", pady=(0, 10))
        
        # Create the chart
        fig = create_expense_pie_chart(self.expenses, self.categories_dict)
        
        # Display the chart in the frame
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.chart_canvas = canvas
        
        # Add top expense categories table
        table_frame = ttk.Frame(container, style="Card.TFrame", padding=10)
        table_frame.pack(pady=20, fill="x", padx=20)
        
        table_title = ttk.Label(table_frame, text="Top Expense Categories", 
                              font=("Helvetica", 12, "bold"))
        table_title.pack(anchor="w", pady=(0, 10))
        
        # Create table
        table = ttk.Frame(table_frame)
        table.pack(fill="x")
        
        # Headers
        ttk.Label(table, text="Category", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Amount Spent", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="% of Total", font=("Helvetica", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Label(table, text="Transactions", font=("Helvetica", 10, "bold")).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Separator(table, orient="horizontal").grid(row=1, column=0, columnspan=4, sticky="ew", pady=5)
        
        # Get category data
        by_category = summary.get('by_category', {})
        categories_sorted = sorted(by_category.items(), key=lambda x: abs(x[1]['amount']), reverse=True)
        
        # Show top 5 categories
        for i, (category, data) in enumerate(categories_sorted[:5]):
            amount = abs(data['amount'])
            percent = (amount / summary['total_expenses']) * 100 if summary['total_expenses'] > 0 else 0
            count = data['count']
            
            ttk.Label(table, text=category).grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(table, text=f"${amount:.2f}").grid(row=i+2, column=1, sticky="w", padx=5, pady=2)
            ttk.Label(table, text=f"{percent:.1f}%").grid(row=i+2, column=2, sticky="w", padx=5, pady=2)
            ttk.Label(table, text=str(count)).grid(row=i+2, column=3, sticky="w", padx=5, pady=2)
    
    def _show_category_distribution(self):
        """Show the category distribution report."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "This report will be available in a future update", "info")
    
    def _show_trend_analysis(self):
        """Show the trend analysis report."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "This report will be available in a future update", "info")
    
    def _show_period_comparison(self):
        """Show the period comparison report."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "This report will be available in a future update", "info")
    
    def _show_spending_patterns(self):
        """Show the spending patterns report."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "This report will be available in a future update", "info")
    
    def _show_budget_progress(self):
        """Show the budget progress report."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "This report will be available in a future update", "info")
    
    def _export_as_pdf(self):
        """Export the current report as PDF."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "PDF export will be available in a future update", "info")
    
    def _export_as_png(self):
        """Export the current report as PNG."""
        # Stub implementation - will be implemented in future
        self.show_message("Coming Soon", "PNG export will be available in a future update", "info")
    
    def refresh_data(self):
        """Refresh the report data and view."""
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.expenses = Expense.get_user_expenses(user_id, self.controller.data_dir)
            categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.categories_dict = {cat.category_id: cat for cat in categories}
            
            # Reload current report
            self._show_monthly_summary()
            self.current_report = "monthly_summary"
        else:
            self.expenses = []
            self.categories_dict = {}
            
            # Show login message
            for widget in self.main_panel.winfo_children():
                widget.destroy()
            
            container = ttk.Frame(self.main_panel)
            container.pack(fill="both", expand=True)
            
            message = ttk.Label(container, text="Please log in to view reports", 
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
        
        # Refresh report data
        self.refresh_data()
