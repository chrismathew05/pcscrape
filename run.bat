@echo off
if not exist venv\ (
    echo Setting up virtual environment and installing requirements...
    mkdir venv
    python -m venv venv
    call venv/Scripts/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt

    echo Running script...
) else (
    echo Environment already set up.
)

python main.py