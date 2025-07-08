#!/usr/bin/env python3
"""
PostgreSQL Data Import Tool

A GUI application for importing data files (CSV, Excel, JSON) 
into PostgreSQL database with dynamic table creation.

Author: Oğuzhan Berke Özdil
Version: 2.0 - Dynamic Import
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.config import DatabaseConfig
    from src.database import DatabaseManager
    from src.data_utils import DataProcessor
except ImportError as e:
    messagebox.showerror("Error", f"Module import failed: {e}\nPlease check installation.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DatabaseSettingsDialog:
    """Database settings configuration dialog."""
    
    def __init__(self, parent, config: DatabaseConfig):
        self.parent = parent
        self.config = config
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Database Configuration")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        self.create_dialog()
        
    def create_dialog(self):
        """Create the dialog interface."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Title
        title_label = ttk.Label(main_frame, text="PostgreSQL Database Settings", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration fields
        self.entries = {}
        fields = [
            ("Host:", "host", self.config.host),
            ("Port:", "port", str(self.config.port)),
            ("Database:", "db_name", self.config.db_name),
            ("Username:", "user", self.config.user),
            ("Password:", "password", self.config.password),
            ("Schema:", "schema_name", self.config.schema_name),
            ("Table:", "table_name", self.config.table_name)
        ]
        
        for i, (label, key, value) in enumerate(fields, 1):
            ttk.Label(main_frame, text=label, font=('Arial', 10)).grid(
                row=i, column=0, sticky="w", pady=5)
            
            entry = ttk.Entry(main_frame, width=25, font=('Arial', 10))
            entry.insert(0, value)
            if key == 'password':
                entry.config(show='*')
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries[key] = entry
        
        # Connection test frame
        test_frame = ttk.LabelFrame(main_frame, text="Connection Test", padding="10")
        test_frame.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        test_frame.columnconfigure(0, weight=1)
        
        # Test button
        test_btn_frame = ttk.Frame(test_frame)
        test_btn_frame.pack(fill="x", pady=(0, 10))
        
        self.test_btn = ttk.Button(test_btn_frame, text="🔍 Test Connection", 
                                  command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT)
        
        self.create_schema_btn = ttk.Button(test_btn_frame, text="🔧 Create Schema/Table", 
                                           command=self.create_schema_table, state="disabled")
        self.create_schema_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Status display
        self.test_status = tk.StringVar()
        self.test_status.set("Click 'Test Connection' to verify database settings")
        self.status_label = ttk.Label(test_frame, textvariable=self.test_status, 
                                     font=('Arial', 10), foreground='blue')
        self.status_label.pack()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields) + 3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Test Connection", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save to .env", 
                  command=self.save_to_env).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", 
                  command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", 
                  command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
    
    def test_connection(self):
        """Test database connection with current settings."""
        try:
            # Disable button during test
            self.test_btn.config(state="disabled")
            self.test_status.set("Testing connection...")
            self.status_label.config(foreground='blue')
            self.dialog.update()
            
            self.update_config()
            db_manager = DatabaseManager(self.config)
            
            if db_manager.test_connection():
                self.test_status.set("✅ Connection successful!")
                self.status_label.config(foreground='green')
                # Enable the create schema/table button
                self.create_schema_btn.config(state="normal")
            else:
                self.test_status.set("❌ Connection failed!")
                self.status_label.config(foreground='red')
                self.create_schema_btn.config(state="disabled")
                
        except Exception as e:
            self.test_status.set(f"❌ Error: {str(e)}")
            self.status_label.config(foreground='red')
            self.create_schema_btn.config(state="disabled")
        finally:
            # Re-enable button
            self.test_btn.config(state="normal")
    
    def create_schema_table(self):
        """Create schema and table if they don't exist."""
        try:
            # Disable button during creation
            self.create_schema_btn.config(state="disabled")
            self.test_status.set("Creating schema and table...")
            self.status_label.config(foreground='blue')
            self.dialog.update()
            
            self.update_config()
            db_manager = DatabaseManager(self.config)
            
            # Test connection first
            if not db_manager.test_connection():
                self.test_status.set("❌ Connection failed - cannot create schema/table")
                self.status_label.config(foreground='red')
                return
            
            # Create a dummy DataFrame to create the table structure
            import pandas as pd
            dummy_df = pd.DataFrame({
                'id': [1],
                'name': ['sample'],
                'value': [100],
                'date': [pd.Timestamp.now()]
            })
            
            # Create the schema and table
            if db_manager.create_dynamic_table(dummy_df):
                # Remove the dummy data
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {self.config.schema_name}.{self.config.table_name}")
                    conn.commit()
                
                self.test_status.set("✅ Schema and table created successfully!")
                self.status_label.config(foreground='green')
                
                # Try to refresh parent database info if available
                try:
                    if hasattr(self.parent, 'refresh_database_info'):
                        self.parent.after(500, self.parent.refresh_database_info)  # Refresh after dialog closes
                except Exception:
                    pass  # Ignore refresh errors
            else:
                self.test_status.set("❌ Failed to create schema/table")
                self.status_label.config(foreground='red')
                
        except Exception as e:
            self.test_status.set(f"❌ Error creating schema/table: {str(e)}")
            self.status_label.config(foreground='red')
        finally:
            # Re-enable button
            self.create_schema_btn.config(state="normal")
    
    def save_to_env(self):
        """Save current settings to .env file."""
        try:
            self.update_config()
            env_content = f"""DB_HOST={self.config.host}
DB_PORT={self.config.port}
DB_NAME={self.config.db_name}
DB_USER={self.config.user}
DB_PASSWORD={self.config.password}
SCHEMA_NAME={self.config.schema_name}
TABLE_NAME={self.config.table_name}
"""
            with open('.env', 'w') as f:
                f.write(env_content)
            messagebox.showinfo("Success", "Settings saved to .env file!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def update_config(self):
        """Update config with current entry values."""
        self.config.host = self.entries["host"].get()
        self.config.port = int(self.entries["port"].get())
        self.config.db_name = self.entries["db_name"].get()
        self.config.user = self.entries["user"].get()
        self.config.password = self.entries["password"].get()
        self.config.schema_name = self.entries["schema_name"].get()
        self.config.table_name = self.entries["table_name"].get()
    
    def ok_clicked(self):
        """Handle OK button click."""
        self.update_config()
        self.result = True
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = False
        self.dialog.destroy()

class DataPreviewDialog:
    """Dialog for previewing data before import."""
    
    def __init__(self, parent, df: pd.DataFrame, filename: str):
        self.parent = parent
        self.df = df
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Data Preview - {filename}")
        self.dialog.geometry("800x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_preview()
    
    def create_preview(self):
        """Create the preview interface."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        info_text = f"Rows: {len(self.df)} | Columns: {len(self.df.columns)}"
        ttk.Label(info_frame, text=info_text, font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Data frame with scrollbars
        data_frame = ttk.Frame(main_frame)
        data_frame.grid(row=1, column=0, sticky="nsew")
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        
        # Create treeview for data display
        tree = ttk.Treeview(data_frame)
        tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure columns
        tree["columns"] = list(self.df.columns)
        tree["show"] = "headings"
        
        # Add column headings
        for col in self.df.columns:
            tree.heading(col, text=str(col))
            tree.column(col, width=100)
        
        # Add data (first 100 rows for performance)
        for i, row in self.df.head(100).iterrows():
            tree.insert("", "end", values=list(row))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(data_frame, orient="horizontal", command=tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Close button
        ttk.Button(main_frame, text="Close", 
                  command=self.dialog.destroy).grid(row=2, column=0, pady=10)

class PostgreSQLImportApp:
    """Main application class with dynamic import capabilities."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PostgreSQL Data Import Tool")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Application state
        self.config = DatabaseConfig()
        self.selected_files = []
        
        # Create UI components
        self.setup_ui()
        
        # Load saved settings if available
        self.load_settings()
        
        logger.info("Application initialized")
    
    def setup_ui(self):
        """Setup the user interface."""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'), foreground='#2c3e50')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        style.configure('Info.TLabel', foreground='#3498db', font=('Arial', 10))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title section
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="PostgreSQL Data Import Tool", style='Title.TLabel')
        title_label.grid(row=0, column=0)
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="Import CSV, Excel, and JSON files with automatic table creation",
                                  style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # File selection section
        file_section = ttk.LabelFrame(main_frame, text="File Selection", padding="15")
        file_section.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        file_section.columnconfigure(0, weight=1)
        
        # File operations frame
        file_ops_frame = ttk.Frame(file_section)
        file_ops_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_ops_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_ops_frame, text="Browse Files", 
                  command=self.browse_files).grid(row=0, column=0, padx=(0, 10))
        
        file_info = ttk.Label(file_ops_frame, 
                             text="Supported: CSV (.csv), Excel (.xlsx, .xls), JSON (.json)",
                             style='Info.TLabel')
        file_info.grid(row=0, column=1, sticky="w")
        
        # Selected files display
        files_label_frame = ttk.Frame(file_section)
        files_label_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        files_label_frame.columnconfigure(0, weight=1)
        
        ttk.Label(files_label_frame, text="Selected Files:", style='Heading.TLabel').grid(
            row=0, column=0, sticky="w")
        
        # File list with operations
        list_frame = ttk.Frame(file_section)
        list_frame.grid(row=2, column=0, sticky="ew")
        list_frame.columnconfigure(0, weight=1)
        
        # Files listbox
        self.files_listbox = tk.Listbox(list_frame, height=6, font=('Arial', 10))
        self.files_listbox.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # File operation buttons
        file_btn_frame = ttk.Frame(list_frame)
        file_btn_frame.grid(row=0, column=1, sticky="ns")
        
        ttk.Button(file_btn_frame, text="Preview", 
                  command=self.preview_file).pack(pady=(0, 5), fill="x")
        ttk.Button(file_btn_frame, text="Remove", 
                  command=self.remove_file).pack(pady=(0, 5), fill="x")
        ttk.Button(file_btn_frame, text="Clear All", 
                  command=self.clear_files).pack(fill="x")
        
        # Progress section
        progress_section = ttk.LabelFrame(main_frame, text="Import Progress", padding="15")
        progress_section.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        progress_section.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_section, variable=self.progress_var, 
                                           maximum=100, length=500)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to import data")
        self.status_label = ttk.Label(progress_section, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.grid(row=1, column=0)
        
        # Database info section with sync status
        db_section = ttk.LabelFrame(main_frame, text="Database Information", padding="15")
        db_section.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        db_section.columnconfigure(0, weight=1)
        
        # Database info display frame
        db_info_frame = ttk.Frame(db_section)
        db_info_frame.grid(row=0, column=0, sticky="ew")
        db_info_frame.columnconfigure(0, weight=1)
        
        self.db_info_var = tk.StringVar()
        self.update_db_info()
        ttk.Label(db_info_frame, textvariable=self.db_info_var, style='Info.TLabel').grid(row=0, column=0, sticky="w")
        
        # Add refresh button next to database info
        self.refresh_btn = ttk.Button(db_info_frame, text="🔄 Refresh", 
                                     command=self.refresh_database_info, width=12)
        self.refresh_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))
        
        # Sync status indicator
        sync_frame = ttk.Frame(db_section)
        sync_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        sync_frame.columnconfigure(0, weight=1)
        
        self.sync_status_var = tk.StringVar()
        self.sync_status_var.set("🔄 Click 'Database Settings' to test connection")
        self.sync_status_label = ttk.Label(sync_frame, textvariable=self.sync_status_var, 
                                          font=('Arial', 9), foreground='gray')
        self.sync_status_label.grid(row=0, column=0, sticky="w")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=(10, 0))
        
        ttk.Button(button_frame, text="Database Settings", 
                  command=self.show_db_settings).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(button_frame, text="Import Data", 
                  command=self.import_data).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(button_frame, text="View Database", 
                  command=self.view_database).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(button_frame, text="Exit", 
                  command=self.exit_app).pack(side=tk.LEFT)
    
    def load_settings(self):
        """Load saved database settings."""
        try:
            if os.path.exists('.env'):
                self.config.load_from_env('.env')
                self.update_db_info()
                logger.info("Settings loaded from .env file")
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
    
    def update_db_info(self):
        """Update database info display."""
        info = f"Database: {self.config.db_name} | Host: {self.config.host}:{self.config.port} | Schema: {self.config.schema_name}"
        self.db_info_var.set(info)
    
    def browse_files(self):
        """Open file browser dialog."""
        filetypes = [
            ("All Supported", "*.csv;*.xlsx;*.xls;*.json"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx;*.xls"),
            ("JSON Files", "*.json"),
            ("All Files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select data files to import",
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    self.files_listbox.insert(tk.END, os.path.basename(file_path))
            
            self.status_var.set(f"Selected {len(self.selected_files)} file(s)")
            logger.info(f"Selected {len(files)} files")
    
    def preview_file(self):
        """Preview selected file data."""
        selection = self.files_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to preview")
            return
        
        file_index = selection[0]
        file_path = self.selected_files[file_index]
        
        try:
            self.status_var.set("Loading file preview...")
            self.root.update()
            
            # Read the file
            processor = DataProcessor()
            file_format = processor.get_file_format(file_path)
            df = processor.read_data_file(file_path, file_format)
            
            # Show preview dialog
            DataPreviewDialog(self.root, df, os.path.basename(file_path))
            
            self.status_var.set("Preview loaded")
            
        except Exception as e:
            self.status_var.set("Preview failed")
            messagebox.showerror("Error", f"Could not preview file: {str(e)}")
    
    def remove_file(self):
        """Remove selected file from list."""
        selection = self.files_listbox.curselection()
        if selection:
            file_index = selection[0]
            self.files_listbox.delete(file_index)
            del self.selected_files[file_index]
            self.status_var.set(f"{len(self.selected_files)} file(s) selected")
    
    def clear_files(self):
        """Clear all selected files."""
        self.files_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.status_var.set("Ready to import data")
    
    def show_db_settings(self):
        """Show database settings dialog."""
        dialog = DatabaseSettingsDialog(self.root, self.config)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.update_db_info()
            self.update_sync_status()
            logger.info("Database settings updated")
    
    def update_sync_status(self):
        """Update the sync status indicator."""
        try:
            db_manager = DatabaseManager(self.config)
            if db_manager.test_connection():
                self.sync_status_var.set("✅ Database connected and ready")
                self.sync_status_label.config(foreground='green')
            else:
                self.sync_status_var.set("❌ Database connection failed")
                self.sync_status_label.config(foreground='red')
        except Exception as e:
            self.sync_status_var.set(f"❌ Connection error: {str(e)[:50]}...")
            self.sync_status_label.config(foreground='red')
    
    def refresh_database_info(self):
        """Refresh database connection and information display."""
        try:
            # Disable refresh button during operation
            self.refresh_btn.config(state="disabled")
            self.sync_status_var.set("🔄 Refreshing database information...")
            self.sync_status_label.config(foreground='blue')
            self.root.update()
            
            # Test connection and update info
            self.update_sync_status()
            self.update_db_info()
            
            # Get additional info about tables
            db_manager = DatabaseManager(self.config)
            if db_manager.test_connection():
                all_tables = db_manager.get_all_tables()
                if all_tables:
                    table_count = len(all_tables)
                    self.sync_status_var.set(f"✅ Connected - {table_count} table(s) found in schema")
                    self.sync_status_label.config(foreground='green')
                else:
                    self.sync_status_var.set("✅ Connected - No tables found in schema")
                    self.sync_status_label.config(foreground='orange')
            
        except Exception as e:
            self.sync_status_var.set(f"❌ Refresh failed: {str(e)[:50]}...")
            self.sync_status_label.config(foreground='red')
        finally:
            # Re-enable refresh button
            self.refresh_btn.config(state="normal")
    
    def import_data(self):
        """Import selected files to database."""
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select files to import")
            return
        
        # Run import in separate thread to avoid UI freezing
        import_thread = threading.Thread(target=self.import_data_thread)
        import_thread.daemon = True
        import_thread.start()
    
    def import_data_thread(self):
        """Import data in separate thread."""
        try:
            self.status_var.set("Starting import process...")
            self.progress_var.set(0)
            
            # Test database connection
            db_manager = DatabaseManager(self.config)
            if not db_manager.test_connection():
                self.status_var.set("Database connection failed")
                messagebox.showerror("Error", "Database connection failed. Please check settings.")
                return
            
            total_files = len(self.selected_files)
            successful_imports = 0
            
            for i, file_path in enumerate(self.selected_files):
                try:
                    filename = os.path.basename(file_path)
                    self.status_var.set(f"Processing {filename}...")
                    
                    # Read and process file
                    processor = DataProcessor()
                    file_format = processor.get_file_format(file_path)
                    df = processor.read_data_file(file_path, file_format)
                    
                    if df.empty:
                        logger.warning(f"File {filename} is empty, skipping")
                        continue
                    
                    # Create dynamic table name based on filename
                    table_name = os.path.splitext(filename)[0].lower()
                    table_name = ''.join(c for c in table_name if c.isalnum() or c == '_')
                    
                    # Import data dynamically
                    if db_manager.insert_dynamic_data(df, table_name):
                        successful_imports += 1
                        logger.info(f"Successfully imported {filename} to table {table_name}")
                    else:
                        logger.error(f"Failed to import {filename}")
                    
                    # Update progress
                    progress = ((i + 1) / total_files) * 100
                    self.progress_var.set(progress)
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    continue
            
            # Final status with clear feedback
            if successful_imports == total_files:
                self.status_var.set(f"✅ Successfully imported {successful_imports}/{total_files} files")
                # Refresh database info automatically after successful import
                self.refresh_database_info()
                messagebox.showinfo("Import Complete", 
                    f"🎉 All {successful_imports} files imported successfully!\n\n"
                    f"Data is now available in your PostgreSQL database.\n"
                    f"Database information has been refreshed.\n"
                    f"Use 'View Database' to see the imported data.")
            elif successful_imports > 0:
                self.status_var.set(f"⚠️ Partial success: {successful_imports}/{total_files} files imported")
                # Refresh database info for partial success too
                self.refresh_database_info()
                messagebox.showwarning("Partial Import", 
                    f"⚠️ Imported {successful_imports} out of {total_files} files.\n\n"
                    f"Some files may have had errors. Check the log for details.\n"
                    f"Database information has been refreshed.\n"
                    f"Use 'View Database' to see the imported data.")
            else:
                self.status_var.set("❌ Import failed - no files imported")
                messagebox.showerror("Import Failed", 
                    "❌ No files were imported successfully.\n\n"
                    "Please check:\n"
                    "• Database connection settings\n"
                    "• File formats and content\n"
                    "• Log file for detailed errors")
            
            self.progress_var.set(100)
            
        except Exception as e:
            self.status_var.set("Import error")
            messagebox.showerror("Error", f"Import failed: {str(e)}")
            logger.error(f"Import error: {e}")
    
    def view_database(self):
        """Show database contents with latest data."""
        try:
            db_manager = DatabaseManager(self.config)
            if not db_manager.test_connection():
                messagebox.showerror("Error", "Database connection failed. Please check settings.")
                return
            
            # Refresh database info first
            self.refresh_database_info()
            
            # Get all tables in the schema
            all_tables = db_manager.get_all_tables()
            
            if not all_tables:
                messagebox.showinfo("Info", f"No tables found in schema '{self.config.schema_name}'\n\nTip: Import some data first or check your schema name in Database Settings.")
                return
            
            # If multiple tables exist, let user choose or show the most recent
            target_table = None
            if len(all_tables) == 1:
                target_table = all_tables[0]
            elif len(all_tables) > 1:
                # Show a selection dialog for multiple tables
                from tkinter import simpledialog
                table_choices = "\n".join([f"{i+1}. {table}" for i, table in enumerate(all_tables)])
                selection = simpledialog.askstring(
                    "Select Table",
                    f"Multiple tables found:\n{table_choices}\n\nEnter table name or number (or press Cancel for most recent):",
                    initialvalue=all_tables[-1]  # Default to last table
                )
                
                if selection is None:
                    target_table = all_tables[-1]  # Most recent if cancelled
                elif selection.isdigit() and 1 <= int(selection) <= len(all_tables):
                    target_table = all_tables[int(selection) - 1]
                elif selection in all_tables:
                    target_table = selection
                else:
                    target_table = all_tables[-1]  # Default fallback
            
            if not target_table:
                messagebox.showerror("Error", "Could not determine target table")
                return
                
            # Update status to show we're loading data
            self.status_var.set(f"Loading data from {target_table}...")
            self.root.update()
            
            # Get table info with fresh connection
            table_info = db_manager.get_table_info(target_table)
            if not table_info.get("exists", False):
                messagebox.showinfo("Info", f"Table '{target_table}' not found.\n\nTry refreshing the database connection.")
                return
            
            # Get sample data (increased limit for better preview)
            sample_data = db_manager.get_sample_data(target_table, limit=100)
            if sample_data is not None and not sample_data.empty:
                table_title = f"Database Table: {self.config.schema_name}.{target_table} ({table_info['record_count']} total records)"
                DataPreviewDialog(self.root, sample_data, table_title)
                self.status_var.set(f"Showing data from {target_table}")
            else:
                # Check if table actually has data with a direct count query
                try:
                    with db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(f"SELECT COUNT(*) FROM {self.config.schema_name}.{target_table}")
                        actual_count = cursor.fetchone()[0]
                        
                    if actual_count > 0:
                        messagebox.showinfo("Info", f"Table '{target_table}' has {actual_count} records but data could not be loaded.\n\nTry refreshing or check table permissions.")
                    else:
                        messagebox.showinfo("Info", f"Table '{target_table}' exists but contains no data.\n\nImport some data first.")
                except Exception as count_error:
                    messagebox.showinfo("Info", f"Table '{target_table}' exists but data status is unclear.\n\nError: {str(count_error)}")
                
                self.status_var.set("Database table appears empty")
                
        except Exception as e:
            self.status_var.set("Database view failed")
            messagebox.showerror("Error", f"Could not view database: {str(e)}\n\nTry refreshing the database connection first.")
            logger.error(f"Database view error: {e}")
    
    def exit_app(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            logger.info("Application shutting down")
            self.root.destroy()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main entry point."""
    try:
        app = PostgreSQLImportApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Critical Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()
