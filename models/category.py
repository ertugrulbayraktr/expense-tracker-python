"""
Category model for the expense tracking system.
This module defines the Category class for managing expense categories.
"""
import json
import os
import uuid
from datetime import datetime


class Category:
    """Category class for organizing expenses into hierarchical categories."""
    
    def __init__(self, name, parent_id=None, category_id=None, color="#3498db", icon=None, 
                 budget=0.0, user_id=None, created_at=None):
        """
        Initialize a new Category instance.
        
        Args:
            name (str): The name of the category.
            parent_id (str, optional): ID of the parent category for hierarchical organization.
            category_id (str, optional): Unique identifier for the category. If not provided, a new UUID will be generated.
            color (str, optional): Hex color code for the category. Defaults to a shade of blue.
            icon (str, optional): Icon identifier for the category.
            budget (float, optional): Monthly budget allocated for this category.
            user_id (str, optional): User ID if this is a user-specific category.
            created_at (str, optional): Creation timestamp. If not provided, current time will be used.
        """
        self.name = name
        self.category_id = category_id if category_id else str(uuid.uuid4())
        self.parent_id = parent_id
        self.color = color
        self.icon = icon
        self.budget = float(budget)
        self.user_id = user_id
        self.created_at = created_at if created_at else datetime.now().isoformat()
    
    def to_dict(self):
        """
        Convert the category object to a dictionary for serialization.
        
        Returns:
            dict: A dictionary representation of the category.
        """
        return {
            "category_id": self.category_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "color": self.color,
            "icon": self.icon,
            "budget": self.budget,
            "user_id": self.user_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Category instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing category data.
            
        Returns:
            Category: A new Category instance.
        """
        return cls(
            name=data.get("name"),
            parent_id=data.get("parent_id"),
            category_id=data.get("category_id"),
            color=data.get("color", "#3498db"),
            icon=data.get("icon"),
            budget=data.get("budget", 0.0),
            user_id=data.get("user_id"),
            created_at=data.get("created_at")
        )
    
    def save(self, data_dir="data"):
        """
        Save the category data to a JSON file.
        
        Args:
            data_dir (str): Directory path for storing category data.
            
        Returns:
            bool: True if saving was successful, False otherwise.
        """
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Create categories directory if it doesn't exist
        categories_dir = os.path.join(data_dir, "categories")
        os.makedirs(categories_dir, exist_ok=True)
        
        # Determine the file path based on whether it's a user-specific or global category
        if self.user_id:
            user_categories_dir = os.path.join(categories_dir, self.user_id)
            os.makedirs(user_categories_dir, exist_ok=True)
            category_file = os.path.join(user_categories_dir, f"{self.category_id}.json")
        else:
            category_file = os.path.join(categories_dir, f"{self.category_id}.json")
        
        try:
            with open(category_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving category data: {e}")
            return False
    
    @classmethod
    def load(cls, category_id, user_id=None, data_dir="data"):
        """
        Load a category from a JSON file.
        
        Args:
            category_id (str): The ID of the category to load.
            user_id (str, optional): The user ID if loading a user-specific category.
            data_dir (str): Directory path for stored category data.
            
        Returns:
            Category: A Category instance if found, None otherwise.
        """
        categories_dir = os.path.join(data_dir, "categories")
        
        # Check user-specific categories first if a user_id is provided
        if user_id:
            user_category_file = os.path.join(categories_dir, user_id, f"{category_id}.json")
            if os.path.exists(user_category_file):
                try:
                    with open(user_category_file, 'r') as f:
                        data = json.load(f)
                    return cls.from_dict(data)
                except Exception as e:
                    print(f"Error loading user category data: {e}")
        
        # Check global categories
        category_file = os.path.join(categories_dir, f"{category_id}.json")
        if os.path.exists(category_file):
            try:
                with open(category_file, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
            except Exception as e:
                print(f"Error loading category data: {e}")
        
        return None
    
    @staticmethod
    def get_all_categories(user_id=None, data_dir="data", include_global=True):
        """
        Get a list of all categories available for a user.
        
        Args:
            user_id (str, optional): User ID to filter user-specific categories.
            data_dir (str): Directory path for stored category data.
            include_global (bool): Whether to include global categories.
            
        Returns:
            list: A list of Category instances.
        """
        categories = []
        categories_dir = os.path.join(data_dir, "categories")
        
        # Return empty list if directory doesn't exist
        if not os.path.exists(categories_dir):
            return categories
        
        # Load global categories if requested
        if include_global:
            for filename in os.listdir(categories_dir):
                if filename.endswith(".json"):
                    category_id = filename.split(".")[0]
                    category = Category.load(category_id, data_dir=data_dir)
                    if category and not category.user_id:  # Ensure it's a global category
                        categories.append(category)
        
        # Load user-specific categories if a user_id is provided
        if user_id:
            user_categories_dir = os.path.join(categories_dir, user_id)
            if os.path.exists(user_categories_dir):
                for filename in os.listdir(user_categories_dir):
                    if filename.endswith(".json"):
                        category_id = filename.split(".")[0]
                        category = Category.load(category_id, user_id, data_dir)
                        if category:
                            categories.append(category)
        
        return categories
    
    @staticmethod
    def create_default_categories(user_id=None, data_dir="data"):
        """
        Create a set of default categories.
        
        Args:
            user_id (str, optional): User ID if creating user-specific categories.
            data_dir (str): Directory path for storing category data.
            
        Returns:
            list: A list of created Category instances.
        """
        default_categories = [
            # Main categories
            {"name": "Housing", "color": "#e74c3c", "budget": 0, "icon": "home"},
            {"name": "Transportation", "color": "#3498db", "budget": 0, "icon": "car"},
            {"name": "Food", "color": "#2ecc71", "budget": 0, "icon": "utensils"},
            {"name": "Utilities", "color": "#f39c12", "budget": 0, "icon": "bolt"},
            {"name": "Healthcare", "color": "#9b59b6", "budget": 0, "icon": "medkit"},
            {"name": "Personal", "color": "#1abc9c", "budget": 0, "icon": "user"},
            {"name": "Entertainment", "color": "#e67e22", "budget": 0, "icon": "film"},
            {"name": "Education", "color": "#34495e", "budget": 0, "icon": "graduation-cap"},
            {"name": "Savings", "color": "#27ae60", "budget": 0, "icon": "piggy-bank"},
            {"name": "Income", "color": "#16a085", "budget": 0, "icon": "money-bill"},
        ]
        
        # Sub-categories - will be created after main categories
        subcategories = [
            # Housing subcategories
            {"name": "Rent/Mortgage", "parent": "Housing", "icon": "building"},
            {"name": "Home Insurance", "parent": "Housing", "icon": "shield-alt"},
            {"name": "Property Tax", "parent": "Housing", "icon": "file-invoice-dollar"},
            {"name": "Repairs", "parent": "Housing", "icon": "tools"},
            {"name": "Furniture", "parent": "Housing", "icon": "couch"},
            
            # Transportation subcategories
            {"name": "Car Payment", "parent": "Transportation", "icon": "car-side"},
            {"name": "Fuel", "parent": "Transportation", "icon": "gas-pump"},
            {"name": "Insurance", "parent": "Transportation", "icon": "shield-alt"},
            {"name": "Maintenance", "parent": "Transportation", "icon": "wrench"},
            {"name": "Public Transit", "parent": "Transportation", "icon": "bus"},
            
            # Food subcategories
            {"name": "Groceries", "parent": "Food", "icon": "shopping-cart"},
            {"name": "Restaurants", "parent": "Food", "icon": "utensils"},
            {"name": "Fast Food", "parent": "Food", "icon": "hamburger"},
            {"name": "Coffee Shops", "parent": "Food", "icon": "coffee"},
            
            # Utilities subcategories
            {"name": "Electricity", "parent": "Utilities", "icon": "bolt"},
            {"name": "Water", "parent": "Utilities", "icon": "tint"},
            {"name": "Gas", "parent": "Utilities", "icon": "fire"},
            {"name": "Internet", "parent": "Utilities", "icon": "wifi"},
            {"name": "Phone", "parent": "Utilities", "icon": "phone"},
            
            # Healthcare subcategories
            {"name": "Insurance", "parent": "Healthcare", "icon": "shield-alt"},
            {"name": "Medications", "parent": "Healthcare", "icon": "pills"},
            {"name": "Doctor", "parent": "Healthcare", "icon": "user-md"},
            {"name": "Dental", "parent": "Healthcare", "icon": "tooth"},
            
            # Personal subcategories
            {"name": "Clothing", "parent": "Personal", "icon": "tshirt"},
            {"name": "Gym", "parent": "Personal", "icon": "dumbbell"},
            {"name": "Haircut", "parent": "Personal", "icon": "cut"},
            {"name": "Cosmetics", "parent": "Personal", "icon": "spa"},
            
            # Entertainment subcategories
            {"name": "Movies", "parent": "Entertainment", "icon": "film"},
            {"name": "Music", "parent": "Entertainment", "icon": "music"},
            {"name": "Games", "parent": "Entertainment", "icon": "gamepad"},
            {"name": "Streaming Services", "parent": "Entertainment", "icon": "tv"},
            {"name": "Hobbies", "parent": "Entertainment", "icon": "palette"},
            
            # Education subcategories
            {"name": "Tuition", "parent": "Education", "icon": "university"},
            {"name": "Books", "parent": "Education", "icon": "book"},
            {"name": "Courses", "parent": "Education", "icon": "laptop-code"},
            
            # Savings subcategories
            {"name": "Emergency Fund", "parent": "Savings", "icon": "umbrella"},
            {"name": "Retirement", "parent": "Savings", "icon": "hand-holding-usd"},
            {"name": "Investments", "parent": "Savings", "icon": "chart-line"},
            
            # Income subcategories
            {"name": "Salary", "parent": "Income", "icon": "briefcase"},
            {"name": "Bonus", "parent": "Income", "icon": "gift"},
            {"name": "Interest", "parent": "Income", "icon": "percentage"},
            {"name": "Dividends", "parent": "Income", "icon": "chart-pie"},
        ]
        
        created_categories = []
        parent_map = {}
        
        # Create main categories first
        for cat_data in default_categories:
            category = Category(
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                budget=cat_data["budget"],
                user_id=user_id
            )
            category.save(data_dir)
            created_categories.append(category)
            parent_map[cat_data["name"]] = category.category_id
        
        # Create subcategories with parent references
        for subcat_data in subcategories:
            if subcat_data["parent"] in parent_map:
                parent_id = parent_map[subcat_data["parent"]]
                category = Category(
                    name=subcat_data["name"],
                    parent_id=parent_id,
                    icon=subcat_data["icon"],
                    user_id=user_id
                )
                category.save(data_dir)
                created_categories.append(category)
        
        return created_categories
        
    def get_full_path(self, categories_dict=None, data_dir="data"):
        """
        Get the full hierarchical path of the category (e.g., "Food > Groceries").
        
        Args:
            categories_dict (dict, optional): Dictionary of categories for faster lookup.
            data_dir (str): Directory path for stored category data.
            
        Returns:
            str: The full path of the category.
        """
        if not self.parent_id:
            return self.name
        
        # If categories_dict is not provided, create one for this operation
        if categories_dict is None:
            categories = Category.get_all_categories(self.user_id, data_dir)
            categories_dict = {cat.category_id: cat for cat in categories}
        
        path = [self.name]
        current_cat = self
        
        # Traverse up the hierarchy
        while current_cat.parent_id:
            parent = categories_dict.get(current_cat.parent_id)
            if parent:
                path.append(parent.name)
                current_cat = parent
            else:
                break
        
        # Reverse the path to get parent > child format
        path.reverse()
        return " > ".join(path)
