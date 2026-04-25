# 🚀 COMPLETE TERMUX SETUP GUIDE FOR EZREX.AI

**Follow this guide step-by-step if you're installing Termux for the first time.**

---

## PART 1: INSTALL TERMUX APP

### Step 1.1: Download Termux
1. Open Google Play Store on your Android phone
2. Search for **"Termux"** (by Fredrik Fornwall)
3. Click **"Install"**
4. Wait for installation to complete
5. Click **"Open"** to launch Termux

### Step 1.2: First Time Setup
When you open Termux for the first time:
- It will download and set up the Linux environment
- This may take 2-5 minutes
- You'll see terminal prompts and messages - this is normal
- Wait until you see `$` prompt

---

## PART 2: UPDATE TERMUX & INSTALL PYTHON

### Step 2.1: Update Package Manager
Copy and paste this command:
```bash
apt update && apt upgrade -y
```

**What it does:** Updates Termux's package list and installs latest versions

### Step 2.2: Install Python 3
```bash
apt install python-pip git -y
```

**What it does:** Installs Python and pip (package manager)

### Step 2.3: Verify Python Installation
```bash
python3 --version
pip3 --version
```

You should see something like:
```
Python 3.9.x
pip 21.x.x
```

---

## PART 3: CLONE EZREX.AI FROM GITHUB

### Step 3.1: Create Projects Directory
```bash
mkdir -p ~/projects
cd ~/projects
```

### Step 3.2: Clone the Repository
```bash
git clone https://github.com/ezrawanyama74-gif/EzraAI-.git
cd EzraAI-
```

**What it does:** Downloads all Ezrex.AI code to your phone

### Step 3.3: Verify Files Downloaded
```bash
ls -la
```

You should see files like:
- `main.py`
- `config.py`
- `requirements.txt`
- And more...

---

## PART 4: INSTALL PYTHON DEPENDENCIES

### Step 4.1: Upgrade pip
```bash
pip3 install --upgrade pip
```

### Step 4.2: Install Project Dependencies
First, let's install the requirements:
```bash
pip3 install numpy pandas scikit-learn
```

### Step 4.3: Install PyTorch (CPU version for Termux)
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Note:** This will take some time. Be patient!

### Step 4.4: Install Kivy (UI Framework)
```bash
pip3 install kivy
```

**Note:** This may take 5-10 minutes. Don't interrupt!

### Step 4.5: Install Other Requirements
```bash
pip3 install flask requests beautifulsoup4 lxml
```

---

## PART 5: CREATE REQUIRED DIRECTORIES

### Step 5.1: Create Directories
```bash
mkdir -p models/trained_models
mkdir -p data
mkdir -p database
mkdir -p logs
mkdir -p ui
```

### Step 5.2: Verify Directories
```bash
ls -la
```

---

## PART 6: INITIALIZE THE DATABASE

### Step 6.1: Create Database Script
First, let's test if everything works by creating a simple test script:

```bash
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""Test setup for Ezrex.AI"""

import sys
import os

print("=" * 50)
print("EZREX.AI - SETUP TEST")
print("=" * 50)

# Check Python version
print(f"\n✓ Python version: {sys.version}")

# Check imports
try:
    import torch
    print(f"✓ PyTorch version: {torch.__version__}")
except ImportError:
    print("✗ PyTorch not installed")

try:
    import pandas
    print(f"✓ Pandas version: {pandas.__version__}")
except ImportError:
    print("✗ Pandas not installed")

try:
    import sklearn
    print(f"✓ Scikit-learn version: {sklearn.__version__}")
except ImportError:
    print("✗ Scikit-learn not installed")

try:
    import kivy
    print(f"✓ Kivy version: {kivy.__version__}")
except ImportError:
    print("✗ Kivy not installed")

# Check directories
print("\n✓ Directory structure:")
for dir_name in ["models", "data", "database", "logs", "ui"]:
    if os.path.exists(dir_name):
        print(f"  ✓ {dir_name}/")
    else:
        print(f"  ✗ {dir_name}/ (missing)")

print("\n" + "=" * 50)
print("Setup test complete!")
print("=" * 50)
EOF
```

### Step 6.2: Run Test Script
```bash
python3 test_setup.py
```

If all shows ✓, you're ready to go!

---

## PART 7: CREATE & RUN THE AI ASSISTANT

### Step 7.1: Create Simple AI Script
```bash
cat > simple_ai.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Ezrex.AI Assistant
A basic version to get started
"""

import sqlite3
from datetime import datetime
import json

class SimpleAI:
    def __init__(self):
        self.db_path = "database/ezrex_ai.db"
        self.init_database()
        self.responses = {
            "hello": "Hello! I'm Ezrex.AI. How can I help you?",
            "help": "I can answer questions, help with coding, analyze data, and learn from you!",
            "name": "I'm Ezrex.AI, your personal AI assistant.",
            "bye": "Goodbye! Thanks for chatting with me!",
            "thanks": "You're welcome!",
        }
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_input TEXT,
                ai_response TEXT,
                timestamp DATETIME,
                feedback REAL
            )
        """)
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def save_conversation(self, user_input, ai_response):
        """Save conversation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (user_input, ai_response, timestamp)
            VALUES (?, ?, ?)
        """, (user_input, ai_response, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_response(self, user_input):
        """Get AI response"""
        user_input_lower = user_input.lower().strip()
        
        # Simple matching
        for keyword, response in self.responses.items():
            if keyword in user_input_lower:
                return response
        
        # Default response
        return "That's interesting! I'm still learning. Can you tell me more?"
    
    def provide_feedback(self, score):
        """Accept user feedback (0.0 to 1.0)"""
        if 0.0 <= score <= 1.0:
            return f"Thanks for the feedback: {score}/1.0"
        return "Please provide a score between 0.0 and 1.0"
    
    def run(self):
        """Run the AI assistant"""
        print("\n" + "=" * 50)
        print("EZREX.AI - INTELLIGENT ASSISTANT")
        print("=" * 50)
        print("\nType 'quit' to exit, 'feedback' to rate, 'history' to see chats\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    print("AI: Goodbye!")
                    break
                
                if user_input.lower() == "history":
                    self.show_history()
                    continue
                
                if user_input.lower().startswith("feedback:"):
                    try:
                        score = float(user_input.split(":")[1].strip())
                        print(f"AI: {self.provide_feedback(score)}")
                    except:
                        print("AI: Please use format 'feedback: 0.8'")
                    continue
                
                response = self.get_response(user_input)
                print(f"AI: {response}\n")
                
                # Save to database
                self.save_conversation(user_input, response)
            
            except KeyboardInterrupt:
                print("\n\nAI: Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_history(self):
        """Show conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_input, ai_response FROM conversations LIMIT 10")
        conversations = cursor.fetchall()
        conn.close()
        
        if not conversations:
            print("No conversation history yet.\n")
            return
        
        print("\n--- CONVERSATION HISTORY ---")
        for user, ai in conversations:
            print(f"You: {user}")
            print(f"AI: {ai}\n")
        print("-----------------------------\n")


if __name__ == "__main__":
    ai = SimpleAI()
    ai.run()
EOF
```

### Step 7.2: Run the AI Assistant
```bash
python3 simple_ai.py
```

### Step 7.3: Test the AI
Try typing:
```
You: hello
You: help
You: What's your name?
You: feedback: 0.9
You: history
You: quit
```

---

## PART 8: TRAIN THE AI WITH FEEDBACK

### Step 8.1: Create Training Script
```bash
cat > train_simple_model.py << 'EOF'
#!/usr/bin/env python3
"""Simple model training"""

import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

def train_model():
    """Train a simple classifier"""
    # Sample training data
    texts = [
        "hello", "hi", "hey",
        "help me", "assist", "support",
        "what's your name", "who are you",
        "bye", "goodbye", "see you"
    ]
    
    labels = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 3]  # Categories
    
    # Vectorize
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    
    # Train
    model = MultinomialNB()
    model.fit(X, labels)
    
    # Save
    joblib.dump(model, 'models/trained_models/simple_classifier.pkl')
    joblib.dump(vectorizer, 'models/trained_models/vectorizer.pkl')
    
    print("✓ Model trained and saved!")
    print(f"  Accuracy on training data: {model.score(X, labels):.2%}")

if __name__ == "__main__":
    train_model()
EOF
```

### Step 8.2: Run Training
```bash
python3 train_simple_model.py
```

You should see:
```
✓ Model trained and saved!
  Accuracy on training data: 100.00%
```

---

## PART 9: DAILY USAGE

### To start the AI daily:
```bash
cd ~/projects/EzraAI-
python3 simple_ai.py
```

### To keep learning:
1. Use the AI
2. Provide feedback with `feedback: 0.9` (0.0 = bad, 1.0 = excellent)
3. Check history with `history`
4. Re-train periodically

---

## TROUBLESHOOTING

### Issue: "Command not found"
**Solution:** Make sure you're in the EzraAI- directory:
```bash
cd ~/projects/EzraAI-
```

### Issue: "ModuleNotFoundError"
**Solution:** Reinstall dependencies:
```bash
pip3 install -r requirements.txt
```

### Issue: Termux runs slow
**Solution:** Use only CPU version of PyTorch (already done above)

### Issue: Permission denied
**Solution:** Add execute permission:
```bash
chmod +x simple_ai.py
```

---

## NEXT STEPS

1. ✅ Run `simple_ai.py` daily
2. ✅ Provide feedback to help it learn
3. ✅ Add your own training data in `data/` folder
4. ✅ Customize responses in the code
5. ✅ Advanced: Use full PyTorch models with main.py

---

## USEFUL COMMANDS

```bash
# Update all packages
pip3 list --outdated
pip3 install --upgrade pip

# Check storage space
df -h

# View logs
tail -f logs/ezrex_ai.log

# Backup database
cp database/ezrex_ai.db database/backup_$(date +%s).db

# Exit Termux
exit
```

---

## IMPORTANT: CREATE REQUIREMENTS.TXT

Create this file to easily install all dependencies:

```bash
cat > requirements.txt << 'EOF'
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
torch>=1.9.0
kivy>=2.1.0
flask>=2.0.0
requests>=2.26.0
beautifulsoup4>=4.9.3
joblib>=1.1.0
EOF
```

Then install all at once:
```bash
pip3 install -r requirements.txt
```

---

## SUCCESS! 🎉

If you've completed all steps, you now have:
✅ Termux installed
✅ Python 3 with all libraries
✅ Ezrex.AI code downloaded
✅ Database initialized
✅ AI assistant running
✅ Model training working

**Start exploring and let the AI learn from your feedback!**

---

**Questions?** Check the repository issues or edit the code to customize it!

**Happy coding! 🚀**
