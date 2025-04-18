"""
Login and user management UI components for the expense tracking system.
This module provides UI components for user authentication and profile management.
"""
import tkinter as tk
from tkinter import ttk
import os
from .base import BaseFrame, Tooltip
from models.user import User
from models.category import Category


class LoginFrame(BaseFrame):
    """Login screen for user authentication."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new LoginFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the login screen widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Login form frame
        login_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        login_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # App title
        title_label = ttk.Label(login_frame, text="Expense Tracker", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")
        
        # Username field
        username_label = ttk.Label(login_frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(login_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=1, column=1, sticky="w", pady=5)
        username_entry.focus_set()
        
        # Password field
        password_label = ttk.Label(login_frame, text="Password:")
        password_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="•", width=30)
        password_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Login button
        login_button = ttk.Button(login_frame, text="Login", style="Primary.TButton", 
                                 command=self._handle_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        # Register button
        register_button = ttk.Button(login_frame, text="Create Account", 
                                    command=lambda: self.controller.show_frame("RegisterFrame"))
        register_button.grid(row=4, column=0, columnspan=2)
        
        # Error message label
        self.error_var = tk.StringVar()
        error_label = ttk.Label(login_frame, textvariable=self.error_var, foreground="#e74c3c")
        error_label.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Center the login frame
        for i in range(6):
            login_frame.grid_rowconfigure(i, weight=0)
        login_frame.grid_rowconfigure(6, weight=1)
        
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)
        
        # Bind Enter key to login
        self.bind_all("<Return>", lambda event: self._handle_login())
    
    def _handle_login(self):
        """Handle user login."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.error_var.set("Please enter both username and password")
            return
        
        # Get all users
        users = User.get_all_users(self.controller.data_dir)
        
        # Check if username exists
        user = None
        for u in users:
            if u.username.lower() == username.lower():
                user = u
                break
        
        if not user:
            self.error_var.set("Username not found")
            return
        
        # Verify password
        if not user.check_password(password):
            self.error_var.set("Incorrect password")
            return
        
        # Login successful
        self.error_var.set("")
        self.controller.current_user = user
        
        # Check if user has categories, if not create default categories
        user_categories = Category.get_all_categories(user.user_id, self.controller.data_dir)
        if not user_categories:
            Category.create_default_categories(user.user_id, self.controller.data_dir)
        
        # Show dashboard
        self.controller.show_frame("DashboardFrame")
    
    def reset(self):
        """Reset the login form."""
        self.username_var.set("")
        self.password_var.set("")
        self.error_var.set("")


class RegisterFrame(BaseFrame):
    """Registration screen for new users."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new RegisterFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the registration screen widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Registration form frame
        register_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        register_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # App title
        title_label = ttk.Label(register_frame, text="Create Account", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")
        
        # Username field
        username_label = ttk.Label(register_frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(register_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=1, column=1, sticky="w", pady=5)
        username_entry.focus_set()
        
        # Email field
        email_label = ttk.Label(register_frame, text="Email:")
        email_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(register_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Password field
        password_label = ttk.Label(register_frame, text="Password:")
        password_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(register_frame, textvariable=self.password_var, show="•", width=30)
        password_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Confirm Password field
        confirm_label = ttk.Label(register_frame, text="Confirm Password:")
        confirm_label.grid(row=4, column=0, sticky="w", pady=5)
        
        self.confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(register_frame, textvariable=self.confirm_var, show="•", width=30)
        confirm_entry.grid(row=4, column=1, sticky="w", pady=5)
        
        # Register button
        register_button = ttk.Button(register_frame, text="Create Account", style="Primary.TButton", 
                                    command=self._handle_register)
        register_button.grid(row=5, column=0, columnspan=2, pady=(20, 10))
        
        # Back to login button
        back_button = ttk.Button(register_frame, text="Back to Login", 
                               command=lambda: self.controller.show_frame("LoginFrame"))
        back_button.grid(row=6, column=0, columnspan=2)
        
        # Error message label
        self.error_var = tk.StringVar()
        error_label = ttk.Label(register_frame, textvariable=self.error_var, foreground="#e74c3c")
        error_label.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        # Center the registration frame
        for i in range(8):
            register_frame.grid_rowconfigure(i, weight=0)
        register_frame.grid_rowconfigure(8, weight=1)
        
        register_frame.grid_columnconfigure(0, weight=1)
        register_frame.grid_columnconfigure(1, weight=1)
    
    def _handle_register(self):
        """Handle user registration."""
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        password = self.password_var.get()
        confirm = self.confirm_var.get()
        
        # Validate inputs
        if not username or not password:
            self.error_var.set("Please enter username and password")
            return
        
        if len(username) < 3:
            self.error_var.set("Username must be at least 3 characters")
            return
        
        if email and '@' not in email:
            self.error_var.set("Please enter a valid email address")
            return
        
        if len(password) < 6:
            self.error_var.set("Password must be at least 6 characters")
            return
        
        if password != confirm:
            self.error_var.set("Passwords do not match")
            return
        
        # Check if username already exists
        users = User.get_all_users(self.controller.data_dir)
        for user in users:
            if user.username.lower() == username.lower():
                self.error_var.set("Username already exists")
                return
        
        # Create new user
        try:
            # Ensure data directory exists
            os.makedirs(os.path.join(self.controller.data_dir, "users"), exist_ok=True)
            
            new_user = User(username=username, password=password, email=email)
            if new_user.save(self.controller.data_dir):
                # Create default categories for the new user
                Category.create_default_categories(new_user.user_id, self.controller.data_dir)
                
                # Show success message and go to login
                self.show_message("Success", "Account created successfully!", "info")
                self.reset()
                self.controller.show_frame("LoginFrame")
            else:
                self.error_var.set("Error creating account. Please try again.")
        except Exception as e:
            self.error_var.set(f"Error: {str(e)}")
    
    def reset(self):
        """Reset the registration form."""
        self.username_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.confirm_var.set("")
        self.error_var.set("")


class ProfileFrame(BaseFrame):
    """Profile management screen for users."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new ProfileFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        BaseFrame.__init__(self, parent, controller, *args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the profile management widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Profile form frame
        profile_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=20)
        profile_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # App title
        title_label = ttk.Label(profile_frame, text="Profile Settings", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")
        
        # Username field (readonly)
        username_label = ttk.Label(profile_frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(profile_frame, textvariable=self.username_var, width=30, state="readonly")
        username_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # Email field
        email_label = ttk.Label(profile_frame, text="Email:")
        email_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(profile_frame, textvariable=self.email_var, width=30)
        email_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Currency preference
        currency_label = ttk.Label(profile_frame, text="Currency:")
        currency_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.currency_var = tk.StringVar()
        currency_options = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CNY", "INR"]
        currency_combo = ttk.Combobox(profile_frame, textvariable=self.currency_var, values=currency_options, width=10)
        currency_combo.grid(row=3, column=1, sticky="w", pady=5)
        
        # Theme preference
        theme_label = ttk.Label(profile_frame, text="Theme:")
        theme_label.grid(row=4, column=0, sticky="w", pady=5)
        
        self.theme_var = tk.StringVar()
        theme_options = ["light", "dark", "blue"]
        theme_combo = ttk.Combobox(profile_frame, textvariable=self.theme_var, values=theme_options, width=10)
        theme_combo.grid(row=4, column=1, sticky="w", pady=5)
        
        # Date format preference
        date_label = ttk.Label(profile_frame, text="Date Format:")
        date_label.grid(row=5, column=0, sticky="w", pady=5)
        
        self.date_var = tk.StringVar()
        date_options = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]
        date_combo = ttk.Combobox(profile_frame, textvariable=self.date_var, values=date_options, width=15)
        date_combo.grid(row=5, column=1, sticky="w", pady=5)
        
        # Change password section
        password_section = ttk.Frame(profile_frame)
        password_section.grid(row=6, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        
        password_title = ttk.Label(password_section, text="Change Password", style="Subtitle.TLabel")
        password_title.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        # Current Password field
        current_label = ttk.Label(password_section, text="Current Password:")
        current_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.current_var = tk.StringVar()
        current_entry = ttk.Entry(password_section, textvariable=self.current_var, show="•", width=30)
        current_entry.grid(row=1, column=1, sticky="w", pady=5)
        
        # New Password field
        new_label = ttk.Label(password_section, text="New Password:")
        new_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.new_var = tk.StringVar()
        new_entry = ttk.Entry(password_section, textvariable=self.new_var, show="•", width=30)
        new_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Confirm New Password field
        confirm_label = ttk.Label(password_section, text="Confirm New Password:")
        confirm_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.confirm_var = tk.StringVar()
        confirm_entry = ttk.Entry(password_section, textvariable=self.confirm_var, show="•", width=30)
        confirm_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Button frame
        button_frame = ttk.Frame(profile_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        
        # Save button
        save_button = ttk.Button(button_frame, text="Save Changes", style="Primary.TButton", 
                                command=self._handle_save)
        save_button.pack(side="left", padx=5)
        
        # Change password button
        password_button = ttk.Button(button_frame, text="Change Password", 
                                    command=self._handle_change_password)
        password_button.pack(side="left", padx=5)
        
        # Back button
        back_button = ttk.Button(button_frame, text="Back to Dashboard", 
                                command=lambda: self.controller.show_frame("DashboardFrame"))
        back_button.pack(side="right", padx=5)
        
        # Error message label
        self.error_var = tk.StringVar()
        error_label = ttk.Label(profile_frame, textvariable=self.error_var, foreground="#e74c3c")
        error_label.grid(row=8, column=0, columnspan=2, pady=(10, 0))
        
        # Center the profile frame
        for i in range(9):
            profile_frame.grid_rowconfigure(i, weight=0)
        profile_frame.grid_rowconfigure(9, weight=1)
        
        profile_frame.grid_columnconfigure(0, weight=0)
        profile_frame.grid_columnconfigure(1, weight=1)
    
    def _handle_save(self):
        """Handle saving profile changes."""
        user = self.controller.current_user
        if not user:
            self.error_var.set("You must be logged in to change settings")
            return
        
        # Update email if changed
        email = self.email_var.get().strip()
        if email != user.email:
            if email and '@' not in email:
                self.error_var.set("Please enter a valid email address")
                return
            user.email = email
        
        # Update preferences
        currency = self.currency_var.get()
        theme = self.theme_var.get()
        date_format = self.date_var.get()
        
        user.preferences["currency"] = currency
        user.preferences["theme"] = theme
        user.preferences["date_format"] = date_format
        
        # Save changes
        if user.save(self.controller.data_dir):
            # Apply theme if changed
            if theme != self.controller.current_theme:
                self.controller.apply_theme(theme)
            
            self.show_message("Success", "Profile updated successfully!", "info")
            self.error_var.set("")
        else:
            self.error_var.set("Error saving profile. Please try again.")
    
    def _handle_change_password(self):
        """Handle changing the user's password."""
        user = self.controller.current_user
        if not user:
            self.error_var.set("You must be logged in to change your password")
            return
        
        current = self.current_var.get()
        new_pass = self.new_var.get()
        confirm = self.confirm_var.get()
        
        # Validate inputs
        if not current or not new_pass or not confirm:
            self.error_var.set("Please fill in all password fields")
            return
        
        if not user.check_password(current):
            self.error_var.set("Current password is incorrect")
            return
        
        if len(new_pass) < 6:
            self.error_var.set("New password must be at least 6 characters")
            return
        
        if new_pass != confirm:
            self.error_var.set("New passwords do not match")
            return
        
        # Change password
        user.set_password(new_pass)
        
        # Save changes
        if user.save(self.controller.data_dir):
            self.show_message("Success", "Password changed successfully!", "info")
            self.current_var.set("")
            self.new_var.set("")
            self.confirm_var.set("")
            self.error_var.set("")
        else:
            self.error_var.set("Error changing password. Please try again.")
    
    def update_profile_info(self):
        """Update profile information fields from the current user."""
        user = self.controller.current_user
        if user:
            self.username_var.set(user.username)
            self.email_var.set(user.email or "")
            self.currency_var.set(user.preferences.get("currency", "USD"))
            self.theme_var.set(user.preferences.get("theme", "light"))
            self.date_var.set(user.preferences.get("date_format", "%Y-%m-%d"))
            
            # Clear password fields
            self.current_var.set("")
            self.new_var.set("")
            self.confirm_var.set("")
            self.error_var.set("")
    
    def on_show_frame(self):
        """Called when the frame is shown."""
        self.update_profile_info()
