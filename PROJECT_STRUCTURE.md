# Project Structure

This document describes the organized structure of the Wedding Manager application.

## Directory Structure

```
wedding-system/
│
├── main.py                 # Application entry point
│
├── config/                 # Configuration module
│   ├── __init__.py
│   └── settings.py        # Application settings and environment variables
│
├── database/              # Database layer
│   ├── __init__.py
│   └── wedding_db.py      # Database operations and management
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── converters.py      # Text and number conversion (Khmer to Arabic)
│   └── font_utils.py      # Font detection and configuration
│
└── ui/                    # User interface components
    ├── __init__.py
    ├── message_box.py     # Custom message dialog box
    └── wedding_app.py     # Main application window
```

## Module Descriptions

### config/

Contains all configuration and settings for the application.

- `settings.py`: Loads environment variables, defines database file path, app title, font settings, and handles UTF-8 encoding setup for Windows.

### database/

Handles all database-related operations.

- `wedding_db.py`: Contains the `WeddingDB` class with methods for:
  - Creating and checking database tables
  - Adding guests
  - Fetching all guests
  - Fetching summary statistics

### utils/

Utility functions used throughout the application.

- `converters.py`: Functions for converting Khmer numerals to Arabic numerals
- `font_utils.py`: Font detection logic to find available Khmer fonts on the system

### ui/

User interface components.

- `message_box.py`: Custom Khmer-language message dialog boxes
- `wedding_app.py`: Main application window with:
  - Sidebar for data entry
  - Data table display
  - Excel export functionality

## Benefits of This Structure

1. **Separation of Concerns**: Each module has a clear, single responsibility
2. **Maintainability**: Easy to locate and modify specific functionality
3. **Reusability**: Components can be reused across different parts of the application
4. **Testing**: Each module can be tested independently
5. **Scalability**: Easy to add new features without affecting existing code
6. **Clean Code**: main.py is now simple and easy to understand

## Running the Application

Simply run the main entry point:
1. active venv 
2. run main.py

```bash
venv\Scripts\activate
python main.py
```

The application will automatically:

1. Load configuration from environment variables
2. Detect available Khmer fonts
3. Initialize the database
4. Launch the GUI
