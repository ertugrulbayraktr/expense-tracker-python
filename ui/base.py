"""
Base UI components for the expense tracking system.
This module defines the base UI components and themes.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from PIL import Image, ImageTk


class BaseFrame(ttk.Frame):
    """Base frame class with common functionality for all frames."""
    
    def __init__(self, parent, controller, *args, **kwargs):
        """
        Initialize a new BaseFrame.
        
        Args:
            parent: The parent widget.
            controller: The main application controller.
        """
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller
        self.parent = parent
        self._setup_styles()
    
    def _setup_styles(self):
        """Set up styles for the frame."""
        style = ttk.Style()
        
        # Configure common styles if they don't exist yet
        if not style.theme_names() or "expense_tracker" not in style.theme_names():
            # Frame styles
            style.configure("Card.TFrame", background="#ffffff", relief="raised", borderwidth=1)
            style.configure("Sidebar.TFrame", background="#f0f0f0")
            
            # Label styles
            style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), background="#ffffff")
            style.configure("Subtitle.TLabel", font=("Helvetica", 12), background="#ffffff")
            style.configure("Info.TLabel", font=("Helvetica", 10), background="#ffffff")
            
            # Button styles
            style.configure("Primary.TButton", font=("Helvetica", 10), background="#3498db")
            style.configure("Success.TButton", font=("Helvetica", 10), background="#2ecc71")
            style.configure("Danger.TButton", font=("Helvetica", 10), background="#e74c3c")
            style.configure("Link.TLabel", font=("Helvetica", 10, "underline"), foreground="#3498db")
    
    def show_message(self, title, message, message_type="info"):
        """
        Show a message dialog.
        
        Args:
            title (str): Title of the message dialog.
            message (str): Message to display.
            message_type (str): Type of message (info, warning, error).
        """
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
    
    def ask_yes_no(self, title, message):
        """
        Show a yes/no question dialog.
        
        Args:
            title (str): Title of the dialog.
            message (str): Question to ask.
            
        Returns:
            bool: True if Yes, False if No.
        """
        return messagebox.askyesno(title, message)
    
    def show_file_dialog(self, mode="open", title="Select a file", 
                         filetypes=(("All files", "*.*"),), initial_dir=None):
        """
        Show a file dialog.
        
        Args:
            mode (str): Dialog mode, either "open" or "save".
            title (str): Title of the dialog.
            filetypes (tuple): File types to show.
            initial_dir (str, optional): Initial directory to show.
            
        Returns:
            str: The selected file path, or None if canceled.
        """
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        
        if mode == "open":
            return filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initial_dir)
        else:
            return filedialog.asksaveasfilename(title=title, filetypes=filetypes, initialdir=initial_dir)
    
    def load_image(self, path, size=None):
        """
        Load an image and optionally resize it.
        
        Args:
            path (str): Path to the image file.
            size (tuple, optional): Target size (width, height).
            
        Returns:
            ImageTk.PhotoImage: The loaded image.
        """
        try:
            image = Image.open(path)
            if size:
                image = image.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None


class ScrollableFrame(ttk.Frame):
    """A frame with scrollbars that can contain other widgets."""
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize a new ScrollableFrame.
        
        Args:
            parent: The parent widget.
        """
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create a window inside the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Update scroll region when the size of the scrollable frame changes
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mousewheel events
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def _on_frame_configure(self, event):
        """Update the scroll region based on the frame size."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize the canvas window when the canvas is resized."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel events for scrolling."""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")


class ThemeManager:
    """Class to manage application themes."""
    
    THEMES = {
        "light": {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f0f0f0",
            "bg_accent": "#e0e0e0",
            "fg_primary": "#000000",
            "fg_secondary": "#666666",
            "accent_color": "#3498db",
            "success_color": "#2ecc71",
            "warning_color": "#f39c12",
            "danger_color": "#e74c3c",
            "border_color": "#dddddd"
        },
        "dark": {
            "bg_primary": "#2c3e50",
            "bg_secondary": "#34495e",
            "bg_accent": "#1c2833",
            "fg_primary": "#ecf0f1",
            "fg_secondary": "#bdc3c7",
            "accent_color": "#3498db",
            "success_color": "#2ecc71",
            "warning_color": "#f39c12",
            "danger_color": "#e74c3c",
            "border_color": "#2c3e50"
        },
        "blue": {
            "bg_primary": "#ebf5fb",
            "bg_secondary": "#d6eaf8",
            "bg_accent": "#aed6f1",
            "fg_primary": "#1f618d",
            "fg_secondary": "#2874a6",
            "accent_color": "#3498db",
            "success_color": "#2ecc71",
            "warning_color": "#f39c12",
            "danger_color": "#e74c3c",
            "border_color": "#aed6f1"
        }
    }
    
    @classmethod
    def apply_theme(cls, root, theme_name="light"):
        """
        Apply a theme to the application.
        
        Args:
            root: The root tkinter window.
            theme_name (str): Name of the theme to apply.
        """
        if theme_name not in cls.THEMES:
            theme_name = "light"
        
        theme = cls.THEMES[theme_name]
        style = ttk.Style()
        
        # Configure ttk styles
        style.configure("TFrame", background=theme["bg_primary"])
        style.configure("TLabel", background=theme["bg_primary"], foreground=theme["fg_primary"])
        style.configure("TButton", background=theme["accent_color"], foreground=theme["fg_primary"])
        style.configure("TEntry", fieldbackground=theme["bg_secondary"], foreground=theme["fg_primary"])
        style.configure("TCombobox", fieldbackground=theme["bg_secondary"], foreground=theme["fg_primary"])
        
        # Configure custom styles
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), background=theme["bg_primary"], foreground=theme["fg_primary"])
        style.configure("Subtitle.TLabel", font=("Helvetica", 12), background=theme["bg_primary"], foreground=theme["fg_primary"])
        style.configure("Card.TFrame", background=theme["bg_primary"], relief="raised", borderwidth=1)
        style.configure("Sidebar.TFrame", background=theme["bg_secondary"])
        
        # Button variants
        style.configure("Primary.TButton", background=theme["accent_color"])
        style.configure("Success.TButton", background=theme["success_color"])
        style.configure("Danger.TButton", background=theme["danger_color"])
        style.configure("Link.TLabel", foreground=theme["accent_color"], font=("Helvetica", 10, "underline"))
        
        # Configure the root window
        root.configure(background=theme["bg_primary"])
        
        return theme


class Tooltip:
    """A tooltip widget that displays text when hovering over a widget."""
    
    def __init__(self, widget, text, delay=500, bg="#ffffea", fg="#000000", x_offset=10, y_offset=10):
        """
        Initialize a new Tooltip.
        
        Args:
            widget: The widget to attach the tooltip to.
            text (str): Text to display in the tooltip.
            delay (int): Delay in milliseconds before showing the tooltip.
            bg (str): Background color of the tooltip.
            fg (str): Text color of the tooltip.
            x_offset (int): X offset from the cursor.
            y_offset (int): Y offset from the cursor.
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.bg = bg
        self.fg = fg
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.tooltip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)
    
    def schedule(self, event=None):
        """Schedule the tooltip to be shown after a delay."""
        self.id = self.widget.after(self.delay, self.show)
    
    def show(self, event=None):
        """Show the tooltip."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.x_offset
        y += self.widget.winfo_rooty() + self.y_offset
        
        # Create a toplevel window
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        
        # Create a label with the tooltip text
        label = tk.Label(tw, text=self.text, justify="left", background=self.bg, foreground=self.fg,
                        relief="solid", borderwidth=1, padx=5, pady=2, wraplength=250)
        label.pack()
    
    def hide(self, event=None):
        """Hide the tooltip."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
