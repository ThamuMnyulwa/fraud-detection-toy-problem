"""
Script to run the Streamlit app.
"""

import subprocess
import os
import sys


def main():
    """
    Run the Streamlit app.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the app.py file
    app_path = os.path.join(script_dir, "app.py")

    print(f"Starting Streamlit app from {app_path}")

    # Run the Streamlit app
    try:
        subprocess.run(["streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Streamlit not found. Please install it with 'pip install streamlit'.")
        sys.exit(1)


if __name__ == "__main__":
    main()
