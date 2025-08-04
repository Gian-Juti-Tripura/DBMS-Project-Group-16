#!/usr/bin/env python3
"""
PharmaCare Analytics Dashboard - Startup Script
Run this script to start the pharmaceutical data management system
"""

import os
import sys
from app import app

def main():
    """Main function to run the Flask application"""
    print("🚀 Starting PharmaCare Analytics Dashboard...")
    print("📊 Pharmaceutical Data Management System")
    print("-" * 50)
    
    # Check if uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads directory")
    
    # Set environment variables for development
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    try:
        print("🌐 Starting Flask server on http://localhost:5000")
        print("📝 Upload your pharmaceutical CSV/Excel files or use sample data")
        print("🔍 Search, filter, and analyze your pharmaceutical data")
        print("📈 View interactive charts and analytics")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Run the Flask application
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down PharmaCare Analytics Dashboard...")
        print("Thank you for using our pharmaceutical data management system!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting the application: {e}")
        print("Please check your Python environment and dependencies.")
        sys.exit(1)

if __name__ == '__main__':
    main()