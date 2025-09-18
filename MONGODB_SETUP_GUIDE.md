# MongoDB Setup Guide for Text Sentiment Extraction

This guide provides step-by-step instructions to install and configure all required software for the Text Sentiment Extraction application using MongoDB.

## 📋 **Software Requirements**

You need to install 4 pieces of software:
1. **MongoDB Community Server** (Database)
2. **Tesseract OCR** (Text extraction from images)
3. **Ollama** (AI embeddings)
4. **Python Dependencies** (Handled automatically)

---

## 🗄️ **1. MongoDB Community Server Installation**

### **Windows:**
1. **Download MongoDB:**
   - Go to: https://www.mongodb.com/try/download/community
   - Select: `Windows x64`
   - Click: `Download`

2. **Install MongoDB:**
   - Run the downloaded `.msi` file
   - Choose: `Complete` installation
   - ✅ **Check:** "Install MongoDB as a Service"
   - ✅ **Check:** "Run service as Network Service user"
   - ✅ **Check:** "Install MongoDB Compass" (optional GUI)
   - Click: `Install`

3. **Verify Installation:**
   ```bash
   # Open Command Prompt and test:
   mongo --version
   # Or for newer versions:
   mongosh --version
   ```

### **Linux (Ubuntu/Debian):**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update packages and install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### **macOS:**
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

---

## 👁️ **2. Tesseract OCR Installation**

### **Windows:**
1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.x.exe` (latest version)

2. **Install Tesseract:**
   - Run the installer
   - ✅ **Important:** Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
   - ✅ **Check:** "Add to PATH" if available

3. **Add to PATH (if not automatic):**
   - Open: `System Properties` → `Environment Variables`
   - Edit: `PATH` variable
   - Add: `C:\Program Files\Tesseract-OCR`

4. **Verify Installation:**
   ```bash
   tesseract --version
   ```

### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por
```

### **macOS:**
```bash
brew install tesseract
```

---

## 🤖 **3. Ollama Installation**

### **Windows:**
1. **Download Ollama:**
   - Go to: https://ollama.ai/download
   - Click: `Download for Windows`

2. **Install Ollama:**
   - Run the downloaded installer
   - Follow the installation wizard

3. **Install the embedding model:**
   ```bash
   # Open Command Prompt and run:
   ollama pull nomic-embed-text
   ```

### **Linux:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the embedding model
ollama pull nomic-embed-text

# Start Ollama service (if needed)
ollama serve
```

### **macOS:**
```bash
# Download from https://ollama.ai/download or use:
brew install ollama

# Pull the embedding model
ollama pull nomic-embed-text
```

---

## 🐍 **4. Python Project Setup**

### **Step 1: Install Dependencies**
```bash
cd TextSentiment
python install_deps.py
```

### **Step 2: Run MongoDB Setup**
```bash
python setup_mongodb.py
```

### **Step 3: Start the Application**
```bash
python main.py
```

---

## ✅ **Verification Checklist**

Run these commands to verify everything is working:

### **MongoDB:**
```bash
# Test MongoDB connection
mongosh --eval "db.runCommand('ping')"
```

### **Tesseract:**
```bash
# Test Tesseract
tesseract --version
```

### **Ollama:**
```bash
# Test Ollama
ollama list
# Should show "nomic-embed-text" in the list
```

### **Application:**
```bash
# Test the app
python setup_mongodb.py
# Should show all green [OK] messages
```

---

## 🚀 **Quick Start Summary**

1. **Install MongoDB Community Server** → Start service
2. **Install Tesseract OCR** → Add to PATH
3. **Install Ollama** → Pull `nomic-embed-text` model
4. **Run:** `python install_deps.py`
5. **Run:** `python setup_mongodb.py`
6. **Run:** `python main.py`
7. **Open:** http://localhost:8000

---

## 🔧 **Configuration**

### **MongoDB Settings (optional):**
Edit `.env` file if needed:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=textsentiment
```

### **For MongoDB with Authentication:**
```env
MONGODB_URL=mongodb://username:password@localhost:27017
```

---

## 🆘 **Troubleshooting**

### **MongoDB Connection Issues:**
```bash
# Check if MongoDB is running
# Windows:
net start MongoDB

# Linux/macOS:
sudo systemctl status mongod
```

### **Tesseract Not Found:**
- Make sure Tesseract is in your PATH
- Try reinstalling and checking "Add to PATH"

### **Ollama Model Missing:**
```bash
ollama pull nomic-embed-text
```

### **Port Conflicts:**
- MongoDB default port: `27017`
- Ollama default port: `11434`
- App default port: `8000`

---

## 📊 **Default Ports Used**

| Service | Port | Purpose |
|---------|------|---------|
| MongoDB | 27017 | Database |
| Ollama | 11434 | AI Embeddings |
| Web App | 8000 | User Interface |

---

## 🎯 **Next Steps**

After successful setup:
1. **Upload test images** with red titles and black text
2. **Test duplicate detection** by uploading the same title twice
3. **Try semantic search** with bible verses
4. **Browse the records page** to manage your data

The MongoDB version is much simpler to set up than PostgreSQL and provides excellent performance for your use case!