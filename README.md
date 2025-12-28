<div align="center">

# 🕰️ Data Time Machine

### *Git for Your Data Pipelines*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/data-time-machine.svg)](https://pypi.org/project/data-time-machine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Never lose track of your data states again. Roll back, debug, and restore with confidence.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

**Data Time Machine (DTM)** is a revolutionary state management system for data pipelines, inspired by Git's version control philosophy. When complex data transformations fail in production, DTM enables you to snapshot entire data environments and roll back to known-good states instantly.

### Why DTM?

- 🔍 **Debug Complex Failures**: Capture exact data states before and after pipeline runs
- ⏮️ **Instant Rollbacks**: Restore entire environments to previous snapshots in seconds
- 📸 **Automatic Snapshots**: Configure automatic state capture at critical pipeline stages
- 🎯 **Lightweight & Fast**: Content-addressable storage means duplicate data is stored only once
- 🔗 **Git-Like Workflow**: Familiar commands (`init`, `snapshot`, `checkout`, `log`)

---

## ✨ Features

### Core Capabilities

- **🔐 Content-Addressable Storage**: Efficient deduplication using SHA-256 hashing
- **📊 Metadata Tracking**: Complete audit trail of all data state changes
- **🌳 Branch Support**: Manage multiple data environments simultaneously
- **⚡ Fast Restoration**: Quickly restore files from any snapshot
- **🎨 Clean CLI**: Intuitive command-line interface built with Click
- **🧪 Fully Tested**: Comprehensive test suite with pytest

### Command Set

```bash
dtm init                    # Initialize a new DTM repository
dtm snapshot -m "message"   # Snapshot current state
dtm checkout <commit-id>    # Restore to a specific snapshot
dtm log                     # View snapshot history
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from PyPI (Recommended)

The easiest way to install Data Time Machine:

```bash
pip install data-time-machine
```

### Install from Source

For development or to get the latest changes:

```bash
# Clone the repository
git clone https://github.com/azmatsiddique/data-time-machine.git
cd data-time-machine

# Install in editable mode
pip install -e .
```

### Verify Installation

```bash
dtm --help
```

---

## 🏁 Quick Start

### 1️⃣ Initialize Your Data Environment

```bash
cd /path/to/your/data/project
dtm init
```

### 2️⃣ Create Your First Snapshot

```bash
# Make some changes to your data files
echo "id,value" > data.csv
echo "1,100" >> data.csv
echo "2,200" >> data.csv

# Snapshot the current state
dtm snapshot -m "Initial clean dataset"
```

### 3️⃣ Simulate a Data Corruption

```bash
# Oops! Pipeline bug corrupts your data
echo "id,value" > data.csv
echo "1,ERROR" >> data.csv
echo "2,200" >> data.csv
```

### 4️⃣ Roll Back to Safety

```bash
# View your snapshot history
dtm log

# Restore to the last good state
dtm checkout <commit-id>

# Your data is back! ✨
cat data.csv
```

---

## 📖 Documentation

### How It Works

DTM uses a three-tier architecture:

1. **Storage Layer**: Content-addressable blob storage for deduplication
2. **Metadata Layer**: Tracks commits, branches, and file relationships
3. **Controller Layer**: Orchestrates snapshots, checkouts, and workspace management

```
┌─────────────────────────────────────────┐
│           CLI Interface (Click)         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Controller (DTMController)        │
│  • Snapshot creation & restoration      │
│  • High-level workflow orchestration    │
└─────┬────────────────────────┬──────────┘
      │                        │
┌─────▼──────────┐    ┌───────▼──────────┐
│ MetadataManager│    │  StorageEngine   │
│ • Commits      │    │  • Hashing       │
│ • Branches     │    │  • Blobs         │
│ • References   │    │  • Restoration   │
└────────────────┘    └──────────────────┘
```

### Running the Demo
 
> [!TIP]
> **Watch the Demo**: [Click here to watch the demo video](demo/demo.mov)

Experience DTM in action with the included demo script:

```bash
python demo.py
```

This demonstrates:
- ✅ Repository initialization
- ✅ Data state snapshotting
- ✅ Simulated pipeline failure
- ✅ Successful state restoration

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_controller.py -v
```

---

## 🏗️ Project Structure

```
data-time-machine/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── core/
│   │   ├── controller.py   # Main orchestration logic
│   │   ├── metadata.py     # Metadata management
│   │   └── storage.py      # Storage engine
│   └── models/
│       └── schema.py       # Pydantic data models
├── tests/
│   ├── test_controller.py
│   ├── test_metadata.py
│   ├── test_storage.py
│   └── conftest.py
├── demo.py                 # Interactive demonstration
├── pyproject.toml          # Project configuration
└── README.md
```

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **CLI Framework**: Click 8.1+
- **Data Validation**: Pydantic 2.5+
- **Testing**: pytest 7.4+
- **Hashing**: SHA-256 (hashlib)
- **Build System**: Hatchling

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. ✅ Make your changes and add tests
4. ✔️ Ensure all tests pass (`pytest`)
5. 💬 Commit your changes (`git commit -m 'Add amazing feature'`)
6. 📤 Push to your branch (`git push origin feature/amazing-feature`)
7. 🎉 Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/azmatsiddique/data-time-machine.git
cd data-time-machine

# Install in development mode with test dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

---

## 📋 Roadmap

- [ ] Add diff visualization between snapshots
- [ ] Implement remote repository support
- [ ] Add compression for large file storage
- [ ] Create web-based visualization dashboard
- [ ] Support for incremental snapshots
- [ ] Integration with popular data pipeline frameworks (Airflow, Prefect)
- [ ] Cloud storage backends (S3, GCS, Azure Blob)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Azmat Siddique**

- GitHub: [@azmatsiddique](https://github.com/azmatsiddique)
- Project Link: [github.com/azmatsiddique/data-time-machine](https://github.com/azmatsiddique/data-time-machine)

---

## 🙏 Acknowledgments

- Inspired by Git's elegant version control design
- Built with modern Python best practices
- Thanks to the open-source community for amazing tools

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by [Azmat Siddique](https://github.com/azmatsiddique)

</div>
