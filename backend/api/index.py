import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app  # Import your Flask app

# This is what Vercel looks for
handler = app