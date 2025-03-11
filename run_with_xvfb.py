import os
import sys
from xvfbwrapper import Xvfb
from PyQt5.QtWidgets import QApplication
from app.main_window import MainWindow
from app.login_widget import LoginWidget
import logging

def setup_logging():
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main application entry point with virtual display."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger('main')
    
    try:
        # Start virtual display
        with Xvfb() as xvfb:
            # Create application
            app = QApplication(sys.argv)
            
            # Show login dialog first
            login = LoginWidget()
            if login.exec_() != LoginWidget.Accepted:
                logger.info("Login cancelled")
                return
                
            # Create and show main window
            window = MainWindow()
            window.show()
            
            # Start event loop
            sys.exit(app.exec_())
            
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
