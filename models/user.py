"""
User model for the expense tracking system.
This module defines the User class for managing user profiles.
"""
import json
import os
import uuid
import bcrypt
from datetime import datetime


class User:
    """User class for managing user profiles in the expense tracking system."""
    
    def __init__(self, username, password=None, user_id=None, email=None, created_at=None):
        """
        Initialize a new User instance.
        
        Args:
            username (str): The username for the user.
            password (str, optional): The password for the user. If provided, it will be hashed.
            user_id (str, optional): Unique identifier for the user. If not provided, a new UUID will be generated.
            email (str, optional): Email address for the user.
            created_at (str, optional): Creation timestamp. If not provided, current time will be used.
        """
        self.username = username
        self.user_id = user_id if user_id else str(uuid.uuid4())
        self.email = email
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.preferences = {
            "theme": "light",
            "currency": "USD",
            "date_format": "%Y-%m-%d"
        }
        
        # Handle password hashing if provided
        self.password_hash = None
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """
        Set and hash the user's password.
        
        Args:
            password (str): The plain text password to hash and store.
        """
        # Hash the password with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        
        Args:
            password (str): The password to check.
            
        Returns:
            bool: True if the password matches, False otherwise.
        """
        if not self.password_hash:
            return False
        
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def update_preference(self, key, value):
        """
        Update a user preference.
        
        Args:
            key (str): The preference key to update.
            value: The new value for the preference.
        """
        self.preferences[key] = value
    
    def to_dict(self):
        """
        Convert the user object to a dictionary for serialization.
        
        Returns:
            dict: A dictionary representation of the user.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "preferences": self.preferences
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a User instance from a dictionary.
        
        Args:
            data (dict): Dictionary containing user data.
            
        Returns:
            User: A new User instance.
        """
        user = cls(
            username=data.get("username"),
            user_id=data.get("user_id"),
            email=data.get("email"),
            created_at=data.get("created_at")
        )
        user.password_hash = data.get("password_hash")
        user.preferences = data.get("preferences", {})
        return user
    
    def save(self, data_dir="data"):
        """
        Save the user data to a JSON file.
        
        Args:
            data_dir (str): Directory path for storing user data.
            
        Returns:
            bool: True if saving was successful, False otherwise.
        """
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Create users directory if it doesn't exist
        users_dir = os.path.join(data_dir, "users")
        os.makedirs(users_dir, exist_ok=True)
        
        # Save user data to a JSON file
        user_file = os.path.join(users_dir, f"{self.user_id}.json")
        try:
            with open(user_file, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    @classmethod
    def load(cls, user_id, data_dir="data"):
        """
        Load a user from a JSON file.
        
        Args:
            user_id (str): The ID of the user to load.
            data_dir (str): Directory path for stored user data.
            
        Returns:
            User: A User instance if found, None otherwise.
        """
        user_file = os.path.join(data_dir, "users", f"{user_id}.json")
        
        try:
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading user data: {e}")
        
        return None
    
    @staticmethod
    def get_all_users(data_dir="data"):
        """
        Get a list of all users.
        
        Args:
            data_dir (str): Directory path for stored user data.
            
        Returns:
            list: A list of User instances.
        """
        users = []
        users_dir = os.path.join(data_dir, "users")
        
        # Return empty list if directory doesn't exist
        if not os.path.exists(users_dir):
            return users
        
        # Load all user files
        for filename in os.listdir(users_dir):
            if filename.endswith(".json"):
                user_id = filename.split(".")[0]
                user = User.load(user_id, data_dir)
                if user:
                    users.append(user)
        
        return users
