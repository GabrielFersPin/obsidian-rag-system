# 🧠 Obsidian RAG System - User Manual

> **RAG system to transform your Obsidian vault into an intelligent study assistant**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [What is this?](#-what-is-this)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [MCP Integration](#-mcp-integration-model-context-protocol)
- [Usage](#-usage)
- [Use Cases](#-use-cases)
- [Troubleshooting](#-troubleshooting)
- [Architecture](#️-architecture)

---

## 🎯 What is this?

A **Retrieval-Augmented Generation (RAG)** system that allows you to query your personal Obsidian knowledge base using artificial intelligence.

### What problems does it solve?

If you take notes in Obsidian, you probably face:
- ❌ Manually searching through hundreds of notes is slow
- ❌ You forget connections between concepts from different topics
- ❌ You don't leverage all the knowledge you've documented

**With this RAG system:**
- ✅ Instant semantic search across all your notes
- ✅ Find relevant information even when using different words
- ✅ Automatically discover connections between topics
- ✅ Everything runs locally on your PC (privacy guaranteed)

---

## ✨ Features

- 🔍 **Intelligent semantic search**: Find notes by meaning, not just exact word matches
- 📊 **Subject/topic filtering**: Organize your searches by categories (Obsidian tags)
- 💾 **Local vector database**: Your data never leaves your computer
- 🚀 **Fast and efficient**: Optimized embedding model (384 dimensions)
- 📈 **Detailed statistics**: See how many notes you have indexed per topic
- 🔄 **Incremental updates**: Reindex only when you add new notes
- 💬 **Interactive mode**: Conversational interface for multiple queries
- 🔌 **MCP Integration**: Use your vault directly from Claude Desktop and Claude Code

---

## 💻 Requirements

### Minimum system requirements
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.10 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk space**: ~2GB for models and database

### Required software
- Python 3.10+
- pip (Python package manager)
- git (to clone the repository)
- An Obsidian vault with notes in Markdown format

---

## 🚀 Installation

### Step 1: Clone the repository

```bash
git clone https://github.com/GabrielFersPin/obsidian-rag-system.git
cd obsidian-rag-system
```

### Step 2: Create virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (WSL2):
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first installation will download ~1GB of dependencies, including PyTorch and Sentence Transformers.

---

## ⚙️ Configuration

### Step 1: Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Path to your Obsidian vault
OBSIDIAN_VAULT_PATH=/home/your-user/Documents/MyVault

# Embedding model (you can change it if desired)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Directory for the vector database
CHROMA_PERSIST_DIR=./chroma_db
```

### Step 2: Create symbolic link to vault (Optional)

If you prefer not to specify the full path, you can create a symbolic link:

```bash
# Create the data directory if it doesn't exist
mkdir -p data

# Create the symbolic link to your vault
ln -s /path/to/your/obsidian/vault ./data/vault
```

Then in `.env`:
```env
OBSIDIAN_VAULT_PATH=./data/vault
```

### Step 3: Recommended note structure

The system works best if your notes have:

**YAML metadata (optional but recommended):**
```yaml
---
deck: DataScience
tags: [machine-learning, python]
created: 2024-01-15
---
```

The `deck` field is used to filter searches by subject/topic.

---

## 🔌 MCP Integration (Model Context Protocol)

This system includes an MCP server that allows Claude Desktop and Claude Code to search your vault directly from their interface.

### What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to access external tools and data sources. With this integration, Claude can:
- 🔍 Search your Obsidian vault in real-time
- 📊 Get vault statistics
- 📚 List notes by subject
- 💬 Answer questions using your personal knowledge base

### Available MCP Tools

1. **search_vault**: Search for information in your vault
   - Parameters: `query` (required), `deck` (optional filter), `n_results` (1-10)

2. **get_vault_stats**: Get vault statistics
   - Shows total notes, distribution by subject, last indexing time

3. **list_notes_by_deck**: List all notes from a specific subject
   - Parameters: `deck` (Algorithms, Cloud, DataScience, Architecture)

### Setup for Claude Desktop

Claude Desktop allows you to connect local MCP servers. Here's how:

#### Step 1: Locate Claude Desktop config file

The configuration file location depends on your OS:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

#### Step 2: Edit the config file

Open the config file and add your MCP server configuration:

```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "/FULL/PATH/TO/obsidian-rag-system/venv/bin/python",
      "args": [
        "/FULL/PATH/TO/obsidian-rag-system/mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/FULL/PATH/TO/YOUR/VAULT"
      }
    }
  }
}
```

**Important**: Replace the paths with your actual paths:
- `/FULL/PATH/TO/obsidian-rag-system/` → Your project directory
- `/FULL/PATH/TO/YOUR/VAULT` → Your Obsidian vault directory

**Example (macOS/Linux):**
```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "/FULL/PATH/TO/obsidian-rag-system/venv/bin/python",
      "args": [
        "/FULL/PATH/TO/obsidian-rag-system/mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/FULL/PATH/TO/VAULT"
      }
    }
  }
}
```

**Example (Windows):**
```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "C:\\Users\\YourName\\obsidian-rag-system\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\obsidian-rag-system\\mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Users\\YourName\\Documents\\MyVault"
      }
    }
  }
}
```

#### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop completely.

#### Step 4: Verify the connection

In Claude Desktop, you should see a 🔌 icon or tools indicator. You can now ask:

```
"Search my vault for information about QuickSort"
"What are my notes on Docker?"
"Show me statistics of my vault"
```

### Setup for Claude Code (CLI)

Claude Code can also use MCP servers. The setup is different:

#### Step 1: Create MCP config file

Create or edit the MCP configuration file for Claude Code:

**Location:** `~/.config/claude-code/mcp.json` (Linux/macOS) or `%APPDATA%\claude-code\mcp.json` (Windows)

```bash
# Create directory if it doesn't exist
mkdir -p ~/.config/claude-code

# Create or edit the config file
nano ~/.config/claude-code/mcp.json
```

#### Step 2: Add server configuration

```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "/FULL/PATH/TO/obsidian-rag-system/venv/bin/python",
      "args": [
        "/FULL/PATH/TO/obsidian-rag-system/mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/FULL/PATH/TO/YOUR/VAULT",
        "CHROMA_PERSIST_DIR": "/FULL/PATH/TO/obsidian-rag-system/chroma_db"
      }
    }
  }
}
```

**Example (Linux/macOS):**
```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "/home/username/obsidian-rag-system/venv/bin/python",
      "args": [
        "/home/username/obsidian-rag-system/mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/home/username/Documents/MyVault",
        "CHROMA_PERSIST_DIR": "/home/username/obsidian-rag-system/chroma_db"
      }
    }
  }
}
```

**Example (Windows):**
```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "C:\\Users\\YourName\\obsidian-rag-system\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\obsidian-rag-system\\mcp_server.py"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Users\\YourName\\Documents\\MyVault",
        "CHROMA_PERSIST_DIR": "C:\\Users\\YourName\\obsidian-rag-system\\chroma_db"
      }
    }
  }
}
```

#### Step 3: Test the server

You can test if the MCP server works correctly:

```bash
# Activate virtual environment
source /path/to/obsidian-rag-system/venv/bin/activate

# Run the MCP server directly (for testing)
python /path/to/obsidian-rag-system/mcp_server.py
```

If everything is configured correctly, the server should start without errors (it will wait for input via stdio).

#### Step 4: Use in Claude Code

When you start Claude Code, it will automatically load the MCP server. You can use it by asking Claude to search your vault:

```
"Use the obsidian-rag server to search my notes about algorithms"
"Get statistics from my vault using the MCP tool"
```

### Troubleshooting MCP Setup

#### Server not appearing in Claude Desktop

**Problem**: The 🔌 icon doesn't appear or tools aren't available.

**Solutions**:
1. Verify the JSON syntax is correct (no trailing commas, proper quotes)
2. Check that all paths are absolute (not relative like `./` or `~/`)
3. Verify the Python executable exists: `ls /path/to/venv/bin/python`
4. Check the vault path exists: `ls /path/to/vault`
5. Restart Claude Desktop completely (quit and reopen)

#### Error: "ModuleNotFoundError"

**Problem**: Python can't find the required modules.

**Solution**: Make sure you're using the Python from the virtual environment:
```bash
/FULL/PATH/TO/obsidian-rag-system/venv/bin/python
```

Not the system Python (`/usr/bin/python3`).

#### Error: "Vault not indexed"

**Problem**: The vault hasn't been indexed yet.

**Solution**: Run the indexing first:
```bash
cd /path/to/obsidian-rag-system
source venv/bin/activate
python run_rag.py
# Select option 2 to index
```

#### MCP server starts but searches fail

**Problem**: ChromaDB can't find the database.

**Solution**: Add the `CHROMA_PERSIST_DIR` environment variable to your MCP config:
```json
"env": {
  "OBSIDIAN_VAULT_PATH": "/path/to/vault",
  "CHROMA_PERSIST_DIR": "/path/to/obsidian-rag-system/chroma_db"
}
```

#### Testing the MCP server manually

You can test the server manually with a simple script:

```bash
cd /path/to/obsidian-rag-system
source venv/bin/activate

# Run server in test mode
python -c "
import asyncio
from mcp_server import get_rag_system

async def test():
    rag = get_rag_system()
    info = rag.get_system_info()
    print(f'Notes indexed: {info[\"indexed_notes\"]}')

asyncio.run(test())
"
```

### Example Usage with Claude

Once configured, you can interact with your vault naturally:

**Example 1: Search for specific topic**
```
You: "Search my vault for notes about Docker containers"

Claude: *Uses search_vault tool*
Found 3 relevant notes:
1. Docker Introduction.md - Explains containerization...
2. Containers vs VMs.md - Compares containers with VMs...
```

**Example 2: Get vault overview**
```
You: "Show me statistics of my note collection"

Claude: *Uses get_vault_stats tool*
Your vault has 98 indexed notes:
- general: 84 notes
- DataScience: 3 notes
- Algorithms: 2 notes
...
```

**Example 3: Filter by subject**
```
You: "What notes do I have about algorithms?"

Claude: *Uses search_vault with deck filter*
Found notes in Algorithms:
- QuickSort.md
- Binary Search.md
- Sorting Algorithms.md
```

---

## 📖 Usage

### Start the system

```bash
# Make sure the virtual environment is activated
source venv/bin/activate

# Run the main program
python3 run_rag.py
```

### Main menu

When you start, you'll see a menu with the following options:

```
============================================================
MAIN MENU
============================================================
1. 📊 View system statistics
2. 🔄 Index vault (first time or update)
3. 🔍 Interactive search
4. 💬 Single query
5. 🧪 Query examples
6. 🚪 Exit
============================================================
```

### First time: Index your vault

**IMPORTANT**: Before searching, you must index your notes.

1. Select option `2` (Index vault)
2. Confirm that you want to proceed (type `s` and press Enter)
3. Wait while the system processes all your notes
4. Indexing can take 1-10 minutes depending on your vault size

**Indexing process:**
```
⏳ Starting indexing...

📚 Step 1/5: Loading notes from vault...
   ✅ 103 notes loaded

🔍 Step 2/5: Filtering valid notes...
   ✅ 98 valid notes

📝 Step 3/5: Creating collection 'obsidian_notes'...
   ✅ Collection created

🧮 Step 4/5: Generating embeddings...
   ⏳ Processing batch 1/2...
   ⏳ Processing batch 2/2...
   ✅ Embeddings generated

💾 Step 5/5: Storing in ChromaDB...
   ✅ Documents stored

✅ Indexing completed!
   📚 Notes processed: 98
   ⏱️  Total time: 45.32s
```

### View statistics (Option 1)

Shows information about your database:

```
📊 SYSTEM STATISTICS
============================================================
📁 Vault: /home/user/vault
📚 Indexed notes: 98
🕐 Last indexing: 2025-11-18T13:52:45
🧮 Model: sentence-transformers/all-MiniLM-L6-v2
📏 Dimension: 384

🎴 Distribution by subject:
   general                         84 notes
   DataScience                      3 notes
   Algorithms                       2 notes
   Cloud                            5 notes
   Architecture                     2 notes
============================================================
```

### Interactive search (Option 3)

Conversational mode for multiple queries:

```
🔍 INTERACTIVE SEARCH MODE
============================================================
Type 'exit' to return to the main menu

💭 Your question: What is QuickSort?
🎴 Filter by subject (Enter for all): Algorithms

🔍 Searching in 2 notes from Algorithms...

📝 RETRIEVED CONTEXT:
============================================================
QuickSort is an efficient sorting algorithm that uses
the divide and conquer paradigm...

📚 SOURCES:
   1. [Algorithms] QuickSort.md (Relevance: 95%)
   2. [Algorithms] Sorting Algorithms.md (Relevance: 78%)
============================================================

💭 Your question: exit
```

### Single query (Option 4)

For a quick single query:

```
💬 SINGLE QUERY
============================================================
💭 Your question: Explain Docker
🎴 Filter by subject (Enter for all): [Enter]

🔍 Searching...

📝 RETRIEVED CONTEXT:
============================================================
Docker is a container platform that allows packaging
applications with all their dependencies...

📚 SOURCES:
   1. [Cloud] Docker Introduction.md (Relevance: 92%)
   2. [Cloud] Containers vs VMs.md (Relevance: 85%)
============================================================
```

### Predefined examples (Option 5)

Try example queries to familiarize yourself with the system.

---

## 🎓 Use Cases

### 1. Study for an exam

```
💭 Your question: Summarize key concepts of neural networks
🎴 Filter by subject: DataScience
```

The system will find all your notes related to neural networks and show you a consolidated summary.

### 2. Connect concepts between subjects

```
💭 Your question: How does CPU pipeline relate to Docker?
🎴 Filter by subject: [Enter - search all]
```

Discover connections you hadn't noticed between different study areas.

### 3. Remember something you wrote months ago

```
💭 Your question: That note where I talked about algorithmic complexity and examples with trees
🎴 Filter by subject: [Enter]
```

Semantic search helps you find notes even when you don't remember the exact words.

### 4. Prepare presentations

```
💭 Your question: Give me all the important concepts about microservices
🎴 Filter by subject: Cloud
```

Gather information from multiple notes to create complete presentations.

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Problem**: Virtual environment not activated.

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "Vault not found at [path]"

**Problem**: The vault path in `.env` is incorrect.

**Solution**:
1. Verify that the `.env` file exists
2. Verify that `OBSIDIAN_VAULT_PATH` points to the correct folder
3. Verify that the folder exists: `ls /path/to/your/vault`

### System doesn't find notes with certain words

**Problem**: The search is semantic, not literal.

**Explanation**: The system searches by meaning, not exact word matching. If you search for "ML" it might not find notes that say "Machine Learning" unless there's sufficient context.

**Solution**: Use more descriptive phrases instead of abbreviations.

### Indexing takes too long

**Problem**: You have many notes or a slow CPU.

**Solution**:
- It's normal on first indexing (1-10 min)
- The model uses CPU by default for compatibility
- Subsequent indexings will be faster

### "No notes indexed"

**Problem**: You haven't run the indexing.

**Solution**:
1. Go to the main menu
2. Select option `2` (Index vault)
3. Confirm with `s`

### Errors with special characters

**Problem**: Some notes have non-UTF-8 characters.

**Solution**: Make sure your Markdown notes are in UTF-8. In Obsidian this is the standard.

---

## 🏗️ Architecture

### How does it work internally?

```
┌─────────────────────────────────────────────┐
│           OBSIDIAN RAG SYSTEM               │
├─────────────────────────────────────────────┤
│                                             │
│  📝 YOUR OBSIDIAN VAULT                     │
│      └─ Markdown notes                      │
│      └─ YAML metadata (deck, tags)          │
│           ↓                                 │
│  🔍 OBSIDIAN LOADER                         │
│      └─ Reads .md files                     │
│      └─ Extracts metadata                   │
│      └─ Ignores templates/.trash            │
│           ↓                                 │
│  🧮 SENTENCE TRANSFORMERS                   │
│      └─ Converts text to vectors            │
│      └─ Model: all-MiniLM-L6-v2             │
│      └─ Dimension: 384                      │
│           ↓                                 │
│  💾 CHROMADB (Vector Database)              │
│      └─ Stores vectors + metadata           │
│      └─ Similarity search (cosine)          │
│      └─ Local disk persistence              │
│           ↓                                 │
│  🔎 SEARCH SYSTEM                           │
│      └─ Top-K most relevant documents       │
│      └─ Filters by deck/subject             │
│      └─ Ranking by relevance                │
│           ↓                                 │
│  💬 USER INTERFACE                          │
│      └─ Interactive menu                    │
│      └─ Natural language queries            │
│                                             │
└─────────────────────────────────────────────┘
```

### Main components

| Component | Function | Technology |
|-----------|----------|------------|
| **Loader** | Reads and parses Markdown notes | Python + YAML |
| **Embeddings** | Converts text to vectors | Sentence Transformers |
| **Vector DB** | Stores and searches vectors | ChromaDB |
| **RAG Chain** | Orchestrates the entire pipeline | Python |
| **Interface** | User menu | Interactive CLI |

### Query flow

1. **User asks question**: "What is QuickSort?"
2. **Question → Vector**: The question is converted to a 384-dimension vector
3. **Semantic search**: ChromaDB searches for the most similar vectors
4. **Ranking**: Orders results by relevance (cosine similarity)
5. **Response**: Shows the most relevant notes and context

---

## 📁 Project Structure

```
obsidian-rag-system/
├── src/                      # Source code
│   ├── obsidian_loader.py    # Reads Obsidian notes
│   ├── embeddings.py         # Generates vectors
│   ├── vectorstore.py        # Manages ChromaDB
│   └── rag_chain.py          # Complete pipeline
│
├── run_rag.py                # Main script (run this)
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (create this)
├── .env.example              # Configuration template
│
├── venv/                     # Virtual environment (create with python -m venv venv)
├── chroma_db/                # Vector database (created automatically)
└── data/                     # Link to your vault (optional)
    └── vault/                # Symlink to Obsidian
```

---

## 🔄 System Updates

### When you add new notes

```bash
# 1. Run the program
python3 run_rag.py

# 2. Select option 2 (Index vault)

# 3. Confirm reindexing
```

**Note**: The system replaces the complete index. This ensures there are no duplicates.

### Update dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🛡️ Privacy and Security

- ✅ **Everything is local**: Your notes never leave your computer
- ✅ **No telemetry**: ChromaDB may report anonymous statistics, but your data is not shared
- ✅ **No API keys**: No external service API keys required
- ✅ **Open source**: You can audit all the code

---

## 💡 Tips and Best Practices

### 1. Organize your notes with metadata

Add YAML frontmatter to your notes:

```markdown
---
deck: DataScience
tags: [python, jupyter, pandas]
created: 2025-01-15
---

# Introduction to Pandas

Pandas is a library...
```

### 2. Use the `deck` field to categorize

The `deck` field is used to filter searches:

- `deck: DataScience`
- `deck: Algorithms`
- `deck: Cloud`

### 3. Write complete questions

❌ Bad: "quicksort"
✅ Good: "How does the QuickSort algorithm work?"

Semantic search works better with context.

### 4. Reindex periodically

Recommendation: Reindex once a week if you add many notes.

### 5. Clean empty notes or templates

The system automatically ignores:
- Folders named `template` or `.trash`
- Very short notes (< 50 characters)
- `.obsidian` and `.git` files

---

## 📊 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Main language |
| Sentence Transformers | 2.2.0+ | Embedding generation |
| ChromaDB | 0.4.22+ | Vector database |
| PyTorch | 2.0.0+ | ML backend |
| python-dotenv | 1.0.0+ | Environment variables |

---

## 🤝 Contributing

This project is open to contributions:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-functionality`)
3. Commit your changes (`git commit -m 'Add new functionality'`)
4. Push to the branch (`git push origin feature/new-functionality`)
5. Open a Pull Request

---

## 📄 License

MIT License - You are free to use, modify, and distribute this software.

See [LICENSE](LICENSE) for more details.

---

## 📧 Support

If you have problems:

1. Review the [Troubleshooting](#-troubleshooting) section
2. Search in [Issues](https://github.com/GabrielFersPin/obsidian-rag-system/issues)
3. Open a new Issue with:
   - Problem description
   - Steps to reproduce
   - Error logs (if any)
   - Your operating system and Python version

---

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Obsidian](https://obsidian.md/) - Note-taking system
- Niklas Luhmann's Zettelkasten method

---


**Last updated**: November 2025

---

> 💡 **Tip**: If you find this project useful, give it a ⭐ on GitHub and share it with other students who use Obsidian.
