"""
Main application for the expense tracking system.
This module provides the entry point and main application controller.
"""
import tkinter as tk
from tkinter import ttk
import os
import sys
from ui.base import ThemeManager
from ui.login import LoginFrame, RegisterFrame, ProfileFrame
from ui.dashboard import DashboardFrame
from ui.expenses import ExpensesFrame
from ui.categories import CategoriesFrame
from ui.reports import ReportsFrame
from ui.budgets import BudgetsFrame
from models.user import User
from models.category import Category
from models.expense import Expense


class ExpenseTrackerApp(tk.Tk):
    """Main application class for the expense tracking system."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the application."""
        tk.Tk.__init__(self, *args, **kwargs)
        
        # Set application title
        self.title("Expense Tracker")
        self.geometry("1200x700")
        self.minsize(800, 600)
        
        # Set application icon
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass  # Icon not found, use default
        
        # Set data directory
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize user state
        self.current_user = None
        self.current_theme = "light"
        
        # Apply default theme
        self.theme = ThemeManager.apply_theme(self, self.current_theme)
        
        # Create the main container
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create and store all frames
        for F in (LoginFrame, RegisterFrame, DashboardFrame, ExpensesFrame, ProfileFrame, CategoriesFrame, ReportsFrame, BudgetsFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show login frame by default
        self.show_frame("LoginFrame")
    
    def show_frame(self, frame_name):
        """
        Show the specified frame.
        
        Args:
            frame_name (str): Name of the frame to show.
        """
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            
            # Call on_show_frame if it exists
            if hasattr(frame, "on_show_frame"):
                frame.on_show_frame()
    
    def apply_theme(self, theme_name):
        """
        Apply the specified theme to the application.
        
        Args:
            theme_name (str): Name of the theme to apply.
        """
        self.theme = ThemeManager.apply_theme(self, theme_name)
        self.current_theme = theme_name
    
    def reload_frames(self):
        """Reload all frames (recreate them)."""
        # Get the current visible frame
        current_visible = None
        for name, frame in self.frames.items():
            if frame.winfo_viewable():
                current_visible = name
                break
        
        # Get the container
        container = next(iter(self.frames.values())).master
        
        # Destroy all frames
        for frame in self.frames.values():
            frame.destroy()
        
        # Recreate frames
        self.frames = {}
        for F in (LoginFrame, RegisterFrame, DashboardFrame, ExpensesFrame, ProfileFrame, CategoriesFrame, ReportsFrame, BudgetsFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show the previously visible frame
        if current_visible:
            self.show_frame(current_visible)


def main():
    """Main entry point for the application."""
    app = ExpenseTrackerApp()
    
    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    try:
        app.mainloop()
    except Exception as e:
        import traceback
        print(f"Unhandled exception: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
