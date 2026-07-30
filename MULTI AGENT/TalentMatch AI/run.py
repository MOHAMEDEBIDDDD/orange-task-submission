import subprocess
import sys
from pathlib import Path

def main():
    """Launch the TalentMatch AI Streamlit frontend."""
    app_path = Path(__file__).resolve().parent / "frontend" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    print(f"🚀 Starting TalentMatch AI on Streamlit...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
