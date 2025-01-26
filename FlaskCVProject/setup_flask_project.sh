#!/bin/bash

# Define absolute root path
PROJECT_ROOT="$(pwd)/FlaskCVProject"

# Create necessary directories and files
mkdir -p "$PROJECT_ROOT"/{static/js,templates}
touch "$PROJECT_ROOT"/{app.py,requirements.txt,.gitignore,README.md}

echo "Verifying directory structure..."
ls -R "$PROJECT_ROOT"

# Function to check file existence and validate content
check_file() {
    local file_path="$1"
    local expected_content="$2"

    if [[ -f "$file_path" ]]; then
        echo "[OK] $file_path exists"
        if [[ -n "$expected_content" ]]; then
            if grep -q "$expected_content" "$file_path"; then
                echo "[OK] Content verification passed for $file_path"
            else
                echo "[ERROR] Content validation failed for $file_path"
            fi
        fi
    else
        echo "[ERROR] $file_path not found!"
        exit 1
    fi
}

# Function to validate directory existence
check_directory() {
    local dir_path="$1"
    if [[ -d "$dir_path" ]]; then
        echo "[OK] Directory $dir_path exists"
    else
        echo "[ERROR] Directory $dir_path does not exist"
        exit 1
    fi
}

# Check files and content validation
check_file "$PROJECT_ROOT/app.py" "Flask"
check_file "$PROJECT_ROOT/requirements.txt" "Flask"
check_file "$PROJECT_ROOT/.gitignore" "venv/"
check_file "$PROJECT_ROOT/README.md" "CV Dashboard"

# Check directories
check_directory "$PROJECT_ROOT/static/js"
check_directory "$PROJECT_ROOT/templates"

# Create virtual environment and install dependencies
python3 -m venv "$PROJECT_ROOT/venv"
source "$PROJECT_ROOT/venv/bin/activate"

if [[ -d "$PROJECT_ROOT/venv" ]]; then
    echo "[OK] Virtual environment created successfully"
else
    echo "[ERROR] Virtual environment setup failed!"
    exit 1
fi

# Install dependencies and validate
pip install Flask Flask-SQLAlchemy qrcode[pil] dash numpy
pip freeze | grep -E 'Flask|SQLAlchemy|qrcode|dash|numpy' > /dev/null

if [[ $? -eq 0 ]]; then
    echo "[OK] Dependencies installed successfully"
else
    echo "[ERROR] Dependency installation failed!"
    exit 1
fi

# Download Chart.js and validate
curl -o "$PROJECT_ROOT/static/js/chart.min.js" https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js
check_file "$PROJECT_ROOT/static/js/chart.min.js" "Chart"

# Create Flask app
cat <<EOF > "$PROJECT_ROOT/app.py"
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
EOF

check_file "$PROJECT_ROOT/app.py" "Flask"

# Create index.html template
cat <<EOF > "$PROJECT_ROOT/templates/index.html"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Dashboard</title>
    <script src="{{ url_for('static', filename='js/chart.min.js') }}"></script>
</head>
<body>
    <h1>Welcome to CV Dashboard</h1>
</body>
</html>
EOF

check_file "$PROJECT_ROOT/templates/index.html" "CV Dashboard"

# Create .gitignore file
cat <<EOF > "$PROJECT_ROOT/.gitignore"
venv/
__pycache__/
*.sqlite
*.pyc
EOF

# Verify .gitignore content
check_file "$PROJECT_ROOT/.gitignore" "venv/"

# Create requirements.txt file
cat <<EOF > "$PROJECT_ROOT/requirements.txt"
Flask
Flask-SQLAlchemy
qrcode[pil]
dash
numpy
EOF

check_file "$PROJECT_ROOT/requirements.txt" "Flask"

# Initialize Git repository
cd "$PROJECT_ROOT"
git init
git add .
git commit -m "Initial FlaskCVProject setup"

# Push to GitHub (optional, add GitHub repo URL)
# git remote add origin https://github.com/yourusername/yourrepository.git
# git push -u origin main

echo "[OK] Project successfully set up in $PROJECT_ROOT"

# Run Flask app for testing
python "$PROJECT_ROOT/app.py" &
sleep 5

# Validate app is running
if curl -s http://127.0.0.1:5000 | grep "CV Dashboard"; then
    echo "[OK] Flask application is running successfully"
else
    echo "[ERROR] Flask did not start correctly"
    exit 1
fi

pkill -f "python $PROJECT_ROOT/app.py"

echo "[OK] Setup completed successfully!"
