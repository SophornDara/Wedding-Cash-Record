"""
Wedding Manager Application
Main entry point for the wedding guest management system.
"""

from ui import WeddingApp


def main():
    """Initialize and run the wedding management application."""
    # Start the application
    app = WeddingApp()
    app.mainloop()


if __name__ == "__main__":
    main()