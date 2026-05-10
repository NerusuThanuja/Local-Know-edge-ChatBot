# University Chatbot - Setup Guide 🎓

Complete setup instructions for the Local Knowledge Chatbot.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Data Preparation](#data-preparation)
5. [Running the Chatbot](#running-the-chatbot)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Windows, macOS, or Linux
- **Python**: 3.9 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 2GB for models and data
- **GPU** (Optional): CUDA 11.0+ for faster inference

### Install Python
Download from [python.org](https://www.python.org/downloads/) and verify:
```bash
python --version  # Should be 3.9+
```

---

## Quick Start

### 1. Clone/Download the Project
```bash
cd c:\Users\varshini.m\OneDrive\Desktop\MLops
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Prepare Data and Embeddings
```bash
# Download and process dataset
python -m src.data_loader

# Generate embeddings (first run only, ~5-10 minutes)
python -m src.embedder

# Build FAISS index
python -m src.retriever
```

### 5. Run Chatbot
```bash
streamlit run app.py
```

The chatbot will open in your browser at `http://localhost:8501`

---

## Detailed Setup

### Step 1: Environment Setup

#### Windows PowerShell
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows CMD
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS/Linux Bash
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; import sentence_transformers; import faiss; print('All dependencies installed!')"
```

### Step 3: Verify Structure
Ensure your project has this structure:
```
MLops/
├── app.py
├── requirements.txt
├── intents.json (optional, will be used as fallback)
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── embedder.py
│   ├── retriever.py
│   ├── chatbot.py
│   └── utils.py
├── assets/
│   └── styles.css
├── data/
│   └── (datasets will be stored here)
├── embeddings/
│   └── (embeddings will be stored here)
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

---

## Data Preparation

### Option 1: Automatic (Recommended)

The system will automatically:
1. Check for Kaggle dataset in `data/` directory
2. Fall back to `intents.json` if available
3. Create a minimal corpus if neither is found

### Option 2: Manual - Using Kaggle Dataset

#### Download via Kaggle API
```bash
# Install Kaggle CLI
pip install kaggle

# Set up credentials (get from https://www.kaggle.com/settings/account)
# Create ~/.kaggle/kaggle.json with your API token

# Download dataset
kaggle datasets download -d tusharpaul2001/university-chatbot-dataset -p data/

# Extract
cd data
unzip university-chatbot-dataset.zip
cd ..
```

#### Download via Kaggle Web UI
1. Go to [Kaggle Dataset](https://www.kaggle.com/datasets/tusharpaul2001/university-chatbot-dataset)
2. Click "Download"
3. Extract to `data/` folder

### Option 3: Use Existing intents.json
The project will automatically use `intents.json` if found in the project root.

---

## Generating Embeddings

On first run, the system automatically generates embeddings. To manually generate:

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Generate embeddings and index
python -m src.data_loader
python -m src.embedder
python -m src.retriever
```

**Expected output:**
```
INFO:__main__:Loaded 1000+ Q&A pairs from dataset
INFO:__main__:Generating embeddings for XXXX texts
INFO:__main__:Generated embeddings with shape: (XXXX, 384)
INFO:__main__:Embeddings saved to embeddings/corpus_embeddings.npy
INFO:__main__:Building FAISS index for XXXX embeddings
INFO:__main__:FAISS index built with XXXX vectors
INFO:__main__:FAISS index saved to embeddings/faiss_index.index
```

**Time Estimates:**
- Data loading: 1-2 seconds
- Embedding generation: 5-15 minutes (depending on corpus size and CPU)
- Index creation: 2-5 seconds

---

## Running the Chatbot

### Development Mode
```bash
streamlit run app.py
```

This will start the development server:
```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

### Production Mode (with Docker)
See [DEPLOY.md](DEPLOY.md)

---

## Testing the Chatbot

Try these test queries:
```
1. "What is admission?"
2. "How to apply to the university?"
3. "Tell me about the fees"
4. "What are the entrance requirements?"
5. "Unknown query xyz" (should return low confidence)
```

---

## Troubleshooting

### Issue: "Module not found" Error

**Solution:**
```bash
# Ensure you're in the correct directory
cd c:\Users\varshini.m\OneDrive\Desktop\MLops

# Activate virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Embeddings File Not Found

**Solution:**
```bash
# Generate embeddings
python -m src.data_loader
python -m src.embedder
python -m src.retriever
```

### Issue: "No module named 'sentence_transformers'"

**Solution:**
```bash
pip install --upgrade sentence-transformers
```

### Issue: FAISS Import Error

**Solution:**
```bash
# Reinstall FAISS
pip uninstall faiss-cpu -y
pip install faiss-cpu
```

### Issue: Streamlit Not Loading

**Solution:**
```bash
# Check if Streamlit is installed
python -c "import streamlit; print(streamlit.__version__)"

# If not, install it
pip install streamlit

# Clear cache
streamlit cache clear
```

### Issue: Out of Memory Error

**Solution:**
- Close other applications
- Reduce batch size in `src/config.py`: `BATCH_SIZE = 16` (from 32)
- If using CPU, consider upgrading RAM

### Issue: Slow Embedding Generation

**Solution:**
This is normal on CPU. Options:
1. **Wait**: Usually completes in 5-15 minutes
2. **Use GPU**: Install PyTorch with CUDA support
3. **Reduce Corpus**: Use smaller dataset for testing

### Issue: Port 8501 Already in Use

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

---

## Configuration

### Modify Embedding Model
Edit `src/config.py`:
```python
# Faster but less accurate
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Slower but more accurate
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

### Adjust Top-K Results
Edit `src/config.py`:
```python
TOP_K = 5  # Number of answers to retrieve
```

### Change Confidence Threshold
Edit `src/config.py`:
```python
SIMILARITY_THRESHOLD = 0.3  # 0-1 scale
```

---

## Performance Tips

1. **First Run**: Embedding generation takes 5-15 minutes. This is one-time only.
2. **Subsequent Runs**: Chatbot loads in ~2-3 seconds
3. **Query Response Time**: ~500ms per query on CPU, ~100ms on GPU

---

## Next Steps

- See [DEPLOY.md](DEPLOY.md) for cloud deployment
- Customize styling in `assets/styles.css`
- Add more features in `src/chatbot.py`
- Integrate with additional data sources

---

## Support

For issues:
1. Check troubleshooting section above
2. Review logs: `python -c "import logging; logging.basicConfig(level=logging.DEBUG)"`
3. Check Python version: `python --version` (should be 3.9+)
