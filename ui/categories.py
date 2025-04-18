"""
Category management UI components for the expense tracking system.
This module provides UI components for creating and managing expense categories.
"""
import tkinter as tk
from tkinter import ttk
import random
from .base import BaseFrame, ScrollableFrame, Tooltip
from models.category import Category


class CategoriesFrame(BaseFrame):
    """Main frame for managing expense categories."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new CategoriesFrame.
        
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
        self.parent_categories = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the category management widgets."""
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
        
        # Show categories list by default
        self._show_categories_list()
    
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
        
        title_label = ttk.Label(title_frame, text="Categories", style="Title.TLabel")
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
        
        # Add category button
        add_btn = ttk.Button(sidebar, text="Add Category", style="Primary.TButton",
                           command=self._show_add_category_dialog)
        add_btn.pack(pady=5, fill="x")
        
        # Filter section
        filter_label = ttk.Label(sidebar, text="Filter Categories", font=("Helvetica", 12, "bold"))
        filter_label.pack(anchor="w", pady=(20, 10))
        
        # View options
        view_frame = ttk.LabelFrame(sidebar, text="View Options")
        view_frame.pack(fill="x", pady=5)
        
        self.view_var = tk.StringVar(value="all")
        
        all_radio = ttk.Radiobutton(view_frame, text="All Categories", value="all", 
                                   variable=self.view_var, command=self._apply_filters)
        all_radio.pack(anchor="w", padx=5, pady=2)
        
        main_radio = ttk.Radiobutton(view_frame, text="Main Categories Only", value="main", 
                                    variable=self.view_var, command=self._apply_filters)
        main_radio.pack(anchor="w", padx=5, pady=2)
        
        # Sort options
        sort_frame = ttk.LabelFrame(sidebar, text="Sort By")
        sort_frame.pack(fill="x", pady=5)
        
        self.sort_var = tk.StringVar(value="name")
        
        name_radio = ttk.Radiobutton(sort_frame, text="Name", value="name", 
                                    variable=self.sort_var, command=self._apply_filters)
        name_radio.pack(anchor="w", padx=5, pady=2)
        
        budget_radio = ttk.Radiobutton(sort_frame, text="Budget", value="budget", 
                                      variable=self.sort_var, command=self._apply_filters)
        budget_radio.pack(anchor="w", padx=5, pady=2)
    
    def _show_categories_list(self):
        """Show the categories list in the main panel."""
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
        
        title_label = ttk.Label(header_frame, text="Manage Categories", style="Title.TLabel")
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
        
        # Create categories container
        categories_frame = ttk.Frame(container, padding=10)
        categories_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        # Display categories as cards
        if self.categories:
            # Group categories by parent
            categorized = {}
            standalone = []
            
            for category in self.categories:
                if not category.parent_id:
                    standalone.append(category)
                else:
                    if category.parent_id not in categorized:
                        categorized[category.parent_id] = []
                    categorized[category.parent_id].append(category)
            
            # Add standalone categories first
            for i, category in enumerate(standalone):
                # Create a card for this category
                self._create_category_card(categories_frame, category, i, categorized.get(category.category_id, []))
        else:
            no_data_label = ttk.Label(categories_frame, text="No categories found",
                                     font=("Helvetica", 12))
            no_data_label.pack(pady=20)
        
        # Add button at the bottom
        bottom_frame = ttk.Frame(container)
        bottom_frame.pack(pady=10, fill="x", padx=20)
        
        add_btn = ttk.Button(bottom_frame, text="Add New Category", 
                           command=self._show_add_category_dialog)
        add_btn.pack(side="left")
        
        refresh_btn = ttk.Button(bottom_frame, text="Refresh", 
                               command=self.refresh_data)
        refresh_btn.pack(side="right")
    
    def _create_category_card(self, parent, category, index, subcategories=None):
        """Create a card for displaying a category and its subcategories."""
        # Create a card frame
        card = ttk.Frame(parent, style="Card.TFrame", padding=10)
        card.pack(fill="x", pady=5)
        
        # Top section with category info
        top_frame = ttk.Frame(card)
        top_frame.pack(fill="x")
        
        # Category color indicator
        color_indicator = tk.Frame(top_frame, width=20, height=20, background=category.color)
        color_indicator.pack(side="left", padx=(0, 10))
        
        # Category name
        name_label = ttk.Label(top_frame, text=category.name, font=("Helvetica", 12, "bold"))
        name_label.pack(side="left")
        
        # Budget info
        budget_label = ttk.Label(top_frame, text=f"Budget: ${category.budget:.2f}")
        budget_label.pack(side="left", padx=20)
        
        # Actions
        actions_frame = ttk.Frame(top_frame)
        actions_frame.pack(side="right")
        
        edit_btn = ttk.Button(actions_frame, text="Edit", width=5,
                            command=lambda c=category: self._show_edit_category_dialog(c))
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ttk.Button(actions_frame, text="Delete", width=5,
                              command=lambda c=category: self._confirm_delete_category(c))
        delete_btn.pack(side="left", padx=2)
        
        # Display subcategories if any
        if subcategories:
            # Add separator
            ttk.Separator(card, orient="horizontal").pack(fill="x", pady=10)
            
            # Subcategories container
            sub_frame = ttk.Frame(card)
            sub_frame.pack(fill="x")
            
            # Configure grid
            columns = 3  # Number of subcategories per row
            for i in range(columns):
                sub_frame.grid_columnconfigure(i, weight=1)
            
            # Add subcategories
            for i, subcat in enumerate(subcategories):
                # Calculate grid position
                row = i // columns
                col = i % columns
                
                # Create subcategory card
                subcat_card = ttk.Frame(sub_frame, padding=5)
                subcat_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                
                # Create color indicator
                sub_color = tk.Frame(subcat_card, width=10, height=10, background=subcat.color)
                sub_color.pack(side="left", padx=(0, 5))
                
                # Subcategory name
                sub_name = ttk.Label(subcat_card, text=subcat.name)
                sub_name.pack(side="left")
                
                # Actions for subcategory
                sub_actions = ttk.Frame(subcat_card)
                sub_actions.pack(side="right")
                
                sub_edit = ttk.Button(sub_actions, text="Edit", width=4,
                                    command=lambda c=subcat: self._show_edit_category_dialog(c))
                sub_edit.pack(side="left", padx=2)
                
                sub_delete = ttk.Button(sub_actions, text="Del", width=4,
                                      command=lambda c=subcat: self._confirm_delete_category(c))
                sub_delete.pack(side="left", padx=2)
            
            # Add new subcategory button
            add_sub_btn = ttk.Button(card, text="Add Subcategory", 
                                   command=lambda c=category: self._show_add_subcategory_dialog(c))
            add_sub_btn.pack(anchor="e", pady=(10, 0))
        else:
            # No subcategories, show add button
            add_sub_btn = ttk.Button(card, text="Add Subcategory", 
                                   command=lambda c=category: self._show_add_subcategory_dialog(c))
            add_sub_btn.pack(anchor="e", pady=(10, 0))
    
    def _show_add_category_dialog(self):
        """Show dialog for adding a new category."""
        # Create a dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Add New Category")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()
        
        # Create form
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Category name
        ttk.Label(frame, text="Category Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        name_entry.focus_set()
        
        # Budget
        ttk.Label(frame, text="Budget:").grid(row=1, column=0, sticky="w", pady=5)
        budget_var = tk.StringVar(value="0.0")
        budget_entry = ttk.Entry(frame, textvariable=budget_var, width=30)
        budget_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Color
        ttk.Label(frame, text="Color:").grid(row=2, column=0, sticky="w", pady=5)
        
        # Generate a random color
        default_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), 
                                                    random.randint(0, 255), 
                                                    random.randint(0, 255))
        color_var = tk.StringVar(value=default_color)
        
        color_preview = tk.Frame(frame, width=30, height=30, bg=default_color)
        color_preview.grid(row=2, column=1, sticky="w", pady=5)
        
        color_btn = ttk.Button(frame, text="Select Color", 
                             command=lambda: self._choose_color(color_var, color_preview))
        color_btn.grid(row=2, column=1, sticky="e", pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Save", 
                            command=lambda: self._save_category(dialog, name_var.get(), 
                                                             budget_var.get(), color_var.get()))
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_add_subcategory_dialog(self, parent_category):
        """Show dialog for adding a subcategory."""
        # Create a dialog window
        dialog = tk.Toplevel(self)
        dialog.title(f"Add Subcategory to {parent_category.name}")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()
        
        # Create form
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Category name
        ttk.Label(frame, text="Subcategory Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        name_entry.focus_set()
        
        # Budget
        ttk.Label(frame, text="Budget:").grid(row=1, column=0, sticky="w", pady=5)
        budget_var = tk.StringVar(value="0.0")
        budget_entry = ttk.Entry(frame, textvariable=budget_var, width=30)
        budget_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Color
        ttk.Label(frame, text="Color:").grid(row=2, column=0, sticky="w", pady=5)
        
        # Generate a random color similar to parent
        parent_color = parent_category.color.lstrip('#')
        parent_rgb = tuple(int(parent_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Slightly vary the color
        new_rgb = tuple(max(0, min(255, c + random.randint(-40, 40))) for c in parent_rgb)
        default_color = "#{:02x}{:02x}{:02x}".format(*new_rgb)
        
        color_var = tk.StringVar(value=default_color)
        
        color_preview = tk.Frame(frame, width=30, height=30, bg=default_color)
        color_preview.grid(row=2, column=1, sticky="w", pady=5)
        
        color_btn = ttk.Button(frame, text="Select Color", 
                             command=lambda: self._choose_color(color_var, color_preview))
        color_btn.grid(row=2, column=1, sticky="e", pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Save", 
                            command=lambda: self._save_subcategory(dialog, name_var.get(), 
                                                                parent_category.category_id,
                                                                budget_var.get(), color_var.get()))
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
    
    def _show_edit_category_dialog(self, category):
        """Show dialog for editing a category."""
        # Create a dialog window
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Category: {category.name}")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()
        
        # Create form
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Category name
        ttk.Label(frame, text="Category Name:").grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value=category.name)
        name_entry = ttk.Entry(frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        name_entry.focus_set()
        
        # Budget
        ttk.Label(frame, text="Budget:").grid(row=1, column=0, sticky="w", pady=5)
        budget_var = tk.StringVar(value=str(category.budget))
        budget_entry = ttk.Entry(frame, textvariable=budget_var, width=30)
        budget_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Color
        ttk.Label(frame, text="Color:").grid(row=2, column=0, sticky="w", pady=5)
        color_var = tk.StringVar(value=category.color)
        
        color_preview = tk.Frame(frame, width=30, height=30, bg=category.color)
        color_preview.grid(row=2, column=1, sticky="w", pady=5)
        
        color_btn = ttk.Button(frame, text="Select Color", 
                             command=lambda: self._choose_color(color_var, color_preview))
        color_btn.grid(row=2, column=1, sticky="e", pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(btn_frame, text="Save", 
                            command=lambda: self._update_category(dialog, category, 
                                                               name_var.get(), 
                                                               budget_var.get(), 
                                                               color_var.get()))
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)
    
    def _choose_color(self, color_var, preview_widget):
        """Show color picker dialog and update the color variable and preview."""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(color_var.get())[1]
            if color:
                color_var.set(color)
                preview_widget.config(bg=color)
        except Exception as e:
            self.show_message("Error", f"Could not open color picker: {str(e)}", "error")
    
    def _save_category(self, dialog, name, budget, color):
        """Save a new category."""
        if not name:
            self.show_message("Error", "Category name cannot be empty", "error")
            return
        
        try:
            budget_value = float(budget)
        except ValueError:
            self.show_message("Error", "Budget must be a number", "error")
            return
        
        # Create and save the category
        user_id = self.controller.current_user.user_id if self.controller.current_user else None
        category = Category(name=name, budget=budget_value, color=color, user_id=user_id)
        
        if category.save(self.controller.data_dir):
            dialog.destroy()
            self.refresh_data()
            self.show_message("Success", "Category added successfully", "info")
        else:
            self.show_message("Error", "Failed to save category", "error")
    
    def _save_subcategory(self, dialog, name, parent_id, budget, color):
        """Save a new subcategory."""
        if not name:
            self.show_message("Error", "Subcategory name cannot be empty", "error")
            return
        
        try:
            budget_value = float(budget)
        except ValueError:
            self.show_message("Error", "Budget must be a number", "error")
            return
        
        # Create and save the subcategory
        user_id = self.controller.current_user.user_id if self.controller.current_user else None
        category = Category(name=name, parent_id=parent_id, budget=budget_value, 
                          color=color, user_id=user_id)
        
        if category.save(self.controller.data_dir):
            dialog.destroy()
            self.refresh_data()
            self.show_message("Success", "Subcategory added successfully", "info")
        else:
            self.show_message("Error", "Failed to save subcategory", "error")
    
    def _update_category(self, dialog, category, name, budget, color):
        """Update an existing category."""
        if not name:
            self.show_message("Error", "Category name cannot be empty", "error")
            return
        
        try:
            budget_value = float(budget)
        except ValueError:
            self.show_message("Error", "Budget must be a number", "error")
            return
        
        # Update category attributes
        category.name = name
        category.budget = budget_value
        category.color = color
        
        if category.save(self.controller.data_dir):
            dialog.destroy()
            self.refresh_data()
            self.show_message("Success", "Category updated successfully", "info")
        else:
            self.show_message("Error", "Failed to update category", "error")
    
    def _confirm_delete_category(self, category):
        """Confirm and delete a category."""
        # Check if the category has subcategories
        subcategories = [cat for cat in self.categories if cat.parent_id == category.category_id]
        
        if subcategories:
            message = f"This category has {len(subcategories)} subcategories that will also be deleted. Are you sure you want to delete '{category.name}' and all its subcategories?"
        else:
            message = f"Are you sure you want to delete the category '{category.name}'?"
        
        if self.ask_yes_no("Confirm Delete", message):
            try:
                # Delete the category
                success = category.delete(self.controller.data_dir)
                
                # Delete subcategories if they exist
                for subcat in subcategories:
                    subcat.delete(self.controller.data_dir)
                
                if success:
                    self.refresh_data()
                    self.show_message("Success", "Category deleted successfully", "info")
                else:
                    self.show_message("Error", "Failed to delete the category", "error")
            except Exception as e:
                self.show_message("Error", f"Error deleting category: {str(e)}", "error")
    
    def _apply_filters(self):
        """Apply filters to the category list."""
        # Stub implementation - will be expanded later
        self._show_categories_list()
    
    def refresh_data(self):
        """Refresh the category data and view."""
        if self.controller.current_user:
            user_id = self.controller.current_user.user_id
            self.categories = Category.get_all_categories(user_id, self.controller.data_dir)
            self.category_dict = {cat.category_id: cat for cat in self.categories}
            
            # Create parent categories dict
            self.parent_categories = {}
            for category in self.categories:
                if not category.parent_id:
                    self.parent_categories[category.category_id] = category
            
            # Apply current filters
            self._apply_filters()
        else:
            self.categories = []
            self.category_dict = {}
            self.parent_categories = {}
            
            # Update UI
            self._show_categories_list()
    
    def on_show_frame(self):
        """Called when the frame is shown."""
        # Update user info
        if self.controller.current_user:
            self.user_var.set(f"Welcome, {self.controller.current_user.username}")
        else:
            self.user_var.set("Welcome, User")
        
        # Refresh categories data
        self.refresh_data()
