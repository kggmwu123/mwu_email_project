import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourcpanelusername/public_html/subdomainname/mybot'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables (optional)
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'ofijancom_ict'
os.environ['DB_PASSWORD'] = 'kebedeguta@ju'
os.environ['DB_NAME'] = 'ofijancom_ict'

# Import your Flask application
from app import app as application  # Adjust the import according to your project structure
