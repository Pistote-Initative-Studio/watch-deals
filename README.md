# Watch Deals

## Setup & Usage

### Prerequisites
- Python 3 installed on your system (macOS or Linux).

Using a virtual environment keeps this project's dependencies isolated, so these steps won't alter your system Python installation.

### Steps

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the environment
source venv/bin/activate

# Install project dependencies
python3 -m pip install -r requirements.txt

# Run the GUI application
python src/gui.py
```

When you're finished, leave the virtual environment with:

```bash
deactivate
```

You can safely delete the `venv` folder at any time to remove the environment without affecting your Mac.
