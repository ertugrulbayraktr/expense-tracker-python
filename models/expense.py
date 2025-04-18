"""
Expense model for the expense tracking system.
This module defines the Expense class for managing expense entries.
"""
import json
import os
import uuid
from datetime import datetime


class Expense:
    """Expense class for tracking individual expense entries."""
    
    def __init__(self, amount, category_id, date=None, description="", expense_id=None, 
                 user_id=None, payment_method=None, recurring=False, recurring_period=None,
                 recurring_end_date=None, tags=None, created_at=None, is_income=False):
        """
        Initialize a new Expense instance.
        
        Args:
            amount (float): The amount of the expense.
            category_id (str): ID of the category this expense belongs to.
            date (str, optional): Date of the expense in ISO format. If not provided, current date will be used.
            description (str, optional): Description of the expense.
            expense_id (str, optional): Unique identifier for the expense. If not provided, a new UUID will be generated.
            user_id (str, optional): ID of the user who owns this expense.
            payment_method (str, optional): Method of payment (e.g., "Cash", "Credit Card").
            recurring (bool, optional): Whether this is a recurring expense.
            recurring_period (str, optional): Period for recurring expenses (e.g., "daily", "weekly", "monthly").
            recurring_end_date (str, optional): End date for recurring expenses in ISO format.
            tags (list, optional): List of tags associated with the expense.
            created_at (str, optional): Creation timestamp. If not provided, current time will be used.
            is_income (bool, optional): Whether this entry represents income rather than an expense.
        """
        self.amount = float(amount)
        self.category_id = category_id
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.description = description
        self.expense_id = expense_id if expense_id else str(uuid.uuid4())
        self.user_id = user_id
        self.payment_method = payment_method
        self.recurring = recurring
        self.recurring_period = recurring_period
        self.recurring_end_date = recurring_end_date
        self.tags = tags if tags else []
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.is_income = is_income
    
    def to_dict(self):
        """
        Convert the expense object to a dictionary for serialization.
        
        Returns:
            dict: A dictionary representation of the expense.
        """
        return {
            "expense_id": self.expense_id,
            "amount": self.amount,
            "category_id": self.category_id,
            "date": self.date,
            "description": self.description,
            "user_id": self.user_id,
            "payment_method": self.payment_method,
            "recurring": self.recurring,
            "recurring_period": self.recurring_period,
            "recurring_end_date": self.recurring_end_date,
            "tags": self.tags,
            "created_at": self.created_at,
            "is_income": self.is_income
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Expense instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing expense data.
            
        Returns:
            Expense: A new Expense instance.
        """
        return cls(
            amount=data.get("amount", 0.0),
            category_id=data.get("category_id"),
            date=data.get("date"),
            description=data.get("description", ""),
            expense_id=data.get("expense_id"),
            user_id=data.get("user_id"),
            payment_method=data.get("payment_method"),
            recurring=data.get("recurring", False),
            recurring_period=data.get("recurring_period"),
            recurring_end_date=data.get("recurring_end_date"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            is_income=data.get("is_income", False)
        )
    
    def save(self, data_dir="data"):
        """
        Save the expense data to a JSON file.
        
        Args:
            data_dir (str): Directory path for storing expense data.
            
        Returns:
            bool: True if saving was successful, False otherwise.
        """
        if not self.user_id:
            print("Error: Cannot save expense without a user_id")
            return False
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Create expenses directory if it doesn't exist
        expenses_dir = os.path.join(data_dir, "expenses")
        os.makedirs(expenses_dir, exist_ok=True)
        
        # Create user-specific expenses directory if it doesn't exist
        user_expenses_dir = os.path.join(expenses_dir, self.user_id)
        os.makedirs(user_expenses_dir, exist_ok=True)
        
        # Save expense data to a JSON file
        expense_file = os.path.join(user_expenses_dir, f"{self.expense_id}.json")
        
        try:
            with open(expense_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving expense data: {e}")
            return False
    
    @classmethod
    def load(cls, expense_id, user_id, data_dir="data"):
        """
        Load an expense from a JSON file.
        
        Args:
            expense_id (str): The ID of the expense to load.
            user_id (str): The ID of the user who owns the expense.
            data_dir (str): Directory path for stored expense data.
            
        Returns:
            Expense: An Expense instance if found, None otherwise.
        """
        expense_file = os.path.join(data_dir, "expenses", user_id, f"{expense_id}.json")
        
        if not os.path.exists(expense_file):
            return None
        
        try:
            with open(expense_file, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading expense data: {e}")
            return None
    
    @staticmethod
    def get_user_expenses(user_id, data_dir="data", start_date=None, end_date=None, 
                          category_id=None, is_income=None):
        """
        Get a list of all expenses for a specific user with optional filtering.
        
        Args:
            user_id (str): The ID of the user.
            data_dir (str): Directory path for stored expense data.
            start_date (str, optional): Start date for filtering in ISO format.
            end_date (str, optional): End date for filtering in ISO format.
            category_id (str, optional): Category ID for filtering.
            is_income (bool, optional): Filter by income or expense type.
            
        Returns:
            list: A list of Expense instances.
        """
        expenses = []
        user_expenses_dir = os.path.join(data_dir, "expenses", user_id)
        
        # Return empty list if directory doesn't exist
        if not os.path.exists(user_expenses_dir):
            return expenses
        
        # Load all expense files
        for filename in os.listdir(user_expenses_dir):
            if filename.endswith(".json"):
                expense_id = filename.split(".")[0]
                expense = Expense.load(expense_id, user_id, data_dir)
                
                if expense:
                    # Apply filters if specified
                    include_expense = True
                    
                    if start_date and expense.date < start_date:
                        include_expense = False
                    
                    if end_date and expense.date > end_date:
                        include_expense = False
                    
                    if category_id and expense.category_id != category_id:
                        include_expense = False
                    
                    if is_income is not None and expense.is_income != is_income:
                        include_expense = False
                    
                    if include_expense:
                        expenses.append(expense)
        
        # Sort expenses by date (most recent first)
        expenses.sort(key=lambda x: x.date, reverse=True)
        
        return expenses
    
    @staticmethod
    def generate_recurring_expenses(user_id, data_dir="data"):
        """
        Generate new instances of recurring expenses if they are due.
        
        Args:
            user_id (str): The ID of the user.
            data_dir (str): Directory path for stored expense data.
            
        Returns:
            list: A list of newly generated Expense instances.
        """
        from datetime import datetime, timedelta
        
        # Get all expenses for the user
        all_expenses = Expense.get_user_expenses(user_id, data_dir)
        
        # Filter to recurring expenses
        recurring_expenses = [exp for exp in all_expenses if exp.recurring]
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        new_expenses = []
        
        for expense in recurring_expenses:
            # Skip if the recurring expense has ended
            if expense.recurring_end_date and expense.recurring_end_date < current_date:
                continue
            
            # Get the most recent instance of this recurring expense
            instances = [exp for exp in all_expenses if exp.description == expense.description 
                        and exp.amount == expense.amount and exp.category_id == expense.category_id]
            
            latest_instance = max(instances, key=lambda x: x.date)
            latest_date = datetime.strptime(latest_instance.date, "%Y-%m-%d")
            
            # Calculate the next instance date based on the recurring period
            next_date = None
            
            if expense.recurring_period == "daily":
                next_date = latest_date + timedelta(days=1)
            elif expense.recurring_period == "weekly":
                next_date = latest_date + timedelta(weeks=1)
            elif expense.recurring_period == "monthly":
                # Simple approach for monthly - add same number of days as in a month
                # This is a simplification and might not always be accurate
                next_date = latest_date.replace(month=latest_date.month % 12 + 1)
                if latest_date.month == 12:
                    next_date = next_date.replace(year=latest_date.year + 1)
            elif expense.recurring_period == "yearly":
                next_date = latest_date.replace(year=latest_date.year + 1)
            
            # If next date is due and not in the future
            if next_date and next_date.strftime("%Y-%m-%d") <= current_date:
                # Create a new expense instance
                new_expense = Expense(
                    amount=expense.amount,
                    category_id=expense.category_id,
                    date=next_date.strftime("%Y-%m-%d"),
                    description=expense.description,
                    user_id=user_id,
                    payment_method=expense.payment_method,
                    recurring=True,
                    recurring_period=expense.recurring_period,
                    recurring_end_date=expense.recurring_end_date,
                    tags=expense.tags,
                    is_income=expense.is_income
                )
                
                # Save the new expense
                new_expense.save(data_dir)
                new_expenses.append(new_expense)
        
        return new_expenses
    
    @staticmethod
    def import_from_csv(file_path, user_id, data_dir="data", category_map=None):
        """
        Import expenses from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file.
            user_id (str): The ID of the user to assign expenses to.
            data_dir (str): Directory path for storing expense data.
            category_map (dict, optional): Mapping of category names to category IDs.
            
        Returns:
            tuple: (success_count, error_count, error_rows)
        """
        import csv
        from datetime import datetime
        
        if not os.path.exists(file_path):
            return 0, 0, []
        
        # If no category map provided, create one
        if not category_map:
            from .category import Category
            categories = Category.get_all_categories(user_id, data_dir)
            category_map = {cat.name.lower(): cat.category_id for cat in categories}
        
        success_count = 0
        error_count = 0
        error_rows = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for i, row in enumerate(reader, start=2):  # Start at 2 to account for header row
                    try:
                        # Extract data from CSV row
                        date_str = row.get('Date', '').strip()
                        amount_str = row.get('Amount', '').strip()
                        category_name = row.get('Category', '').strip()
                        description = row.get('Description', '').strip()
                        
                        # Handle date format
                        try:
                            # Try various date formats
                            date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%d-%m-%Y"]
                            date_obj = None
                            
                            for fmt in date_formats:
                                try:
                                    date_obj = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if date_obj:
                                date = date_obj.strftime("%Y-%m-%d")
                            else:
                                date = datetime.now().strftime("%Y-%m-%d")
                                print(f"Warning: Invalid date format in row {i}, using current date")
                        except Exception:
                            date = datetime.now().strftime("%Y-%m-%d")
                            print(f"Warning: Invalid date format in row {i}, using current date")
                        
                        # Handle amount
                        try:
                            # Remove currency symbols and commas
                            amount_clean = amount_str.replace('$', '').replace('€', '').replace('£', '').replace(',', '')
                            amount = float(amount_clean)
                            is_income = amount > 0
                            # Ensure amount is positive for storage
                            amount = abs(amount)
                        except ValueError:
                            raise ValueError(f"Invalid amount in row {i}: {amount_str}")
                        
                        # Find category ID
                        category_id = None
                        if category_name.lower() in category_map:
                            category_id = category_map[category_name.lower()]
                        else:
                            # Use default category
                            default_categories = [cid for name, cid in category_map.items() 
                                                if name.lower() in ["other", "miscellaneous", "general"]]
                            if default_categories:
                                category_id = default_categories[0]
                            else:
                                # Take first category as fallback
                                if category_map:
                                    category_id = next(iter(category_map.values()))
                                else:
                                    raise ValueError(f"No category found for '{category_name}' in row {i}")
                        
                        # Create and save expense
                        expense = Expense(
                            amount=amount,
                            category_id=category_id,
                            date=date,
                            description=description,
                            user_id=user_id,
                            is_income=is_income
                        )
                        
                        expense.save(data_dir)
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        error_rows.append((i, str(e)))
        
        except Exception as e:
            return 0, 1, [(0, f"Error reading CSV file: {str(e)}")]
        
        return success_count, error_count, error_rows
    
    @staticmethod
    def export_to_csv(file_path, expenses, categories_dict=None):
        """
        Export expenses to a CSV file.
        
        Args:
            file_path (str): Path to save the CSV file.
            expenses (list): List of Expense objects to export.
            categories_dict (dict, optional): Dictionary mapping category IDs to Category objects.
            
        Returns:
            bool: True if export was successful, False otherwise.
        """
        import csv
        
        if not expenses:
            return False
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Date', 'Amount', 'Category', 'Description', 'Payment Method', 'Tags']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for expense in expenses:
                    # Get category name if dictionary provided
                    category_name = ""
                    if categories_dict and expense.category_id in categories_dict:
                        category_name = categories_dict[expense.category_id].name
                    
                    # Format amount (negative for expenses, positive for income)
                    amount = expense.amount
                    if not expense.is_income:
                        amount = -amount
                    
                    # Format tags
                    tags_str = ", ".join(expense.tags) if expense.tags else ""
                    
                    writer.writerow({
                        'Date': expense.date,
                        'Amount': amount,
                        'Category': category_name,
                        'Description': expense.description,
                        'Payment Method': expense.payment_method or "",
                        'Tags': tags_str
                    })
                
            return True
        except Exception as e:
            print(f"Error exporting expenses to CSV: {e}")
            return False
