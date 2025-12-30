<div align="center">

# 🕰️ Data Time Machine

### *Git for Your Data Pipelines*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/data-time-machine.svg)](https://pypi.org/project/data-time-machine/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Never lose track of your data states again. Roll back, debug, and restore with confidence.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Cloud & Remote](#-cloud--remote) • [Dashboard](#-web-dashboard) • [Integrations](#-integrations)

</div>

---

## 🌟 Overview

**Data Time Machine (DTM)** is a revolutionary state management system for data pipelines, inspired by Git's version control philosophy. When complex data transformations fail in production, DTM enables you to snapshot entire data environments and roll back to known-good states instantly.

### Why DTM?

- 🔍 **Debug Complex Failures**: Capture exact data states before and after pipeline runs
- ☁️ **Cloud Native**: Push snapshots to S3, GCS, or Azure Blob Storage
- � **Visual Insights**: Explore commit history and diffs via a built-in Web Dashboard
- ⚡ **Optimized Storage**: Deduplication and gzip compression for handling large datasets efficienty
- � **Pipeline Ready**: Native integrations for Apache Airflow and Prefect

---

## ✨ Features

### Core Capabilities

- **🔐 Content-Addressable Storage**: Efficient deduplication and compression
- **📊 Metadata & Diffs**: View unified diffs of data changes between snapshots
- **⚡ Incremental Snapshots**: Only stores changed files automatically
- **🌐 Remote Support**: Push/Pull to S3, Google Cloud Storage, and Azure Blob
- **🎨 Web Dashboard**: Interactive browser-based visualization of your data history

### Command Set

```bash
dtm init                       # Initialize a new DTM repository
dtm snapshot -m "message"      # Snapshot current state
dtm checkout <commit-id>       # Restore to a specific snapshot
dtm diff <commit_a> <commit_b> # Compare two snapshots
dtm log                        # View snapshot history
dtm web                        # Launch Visualization Dashboard
dtm remote add origin s3://... # Add a remote storage backend
dtm push origin                # Push snapshots to cloud
dtm pull origin                # Pull snapshots from cloud
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from PyPI

```bash
pip install data-time-machine
```

### Install with Cloud Support

To enable S3, GCS, or Azure support, install the necessary extras (conceptually):
```bash
pip install boto3 google-cloud-storage azure-storage-blob
```
*(Or install `fastapi uvicorn` for the dashboard)*

---

## 🏁 Quick Start

### 1️⃣ Initialize
```bash
cd /path/to/data
dtm init
```

### 2️⃣ Snapshot
```bash
echo "important data" > dataset.csv
dtm snapshot -m "Initial baseline"
```

### 3️⃣ Visualize Changes
```bash
echo "bad data" >> dataset.csv
cid=$(dtm snapshot -m "Corrupted run")
dtm diff HEAD^ HEAD
```

### 4️⃣ Use the Dashboard
```bash
dtm web
# Open http://localhost:8000 to browse history visually!
```

---

## ☁️ Cloud & Remote

Push your data snapshots to the cloud for backup or sharing.

```bash
# S3
dtm remote add s3-backup s3://my-bucket/dtm-repo
dtm push s3-backup

# Google Cloud Storage
dtm remote add gcs-origin gs://my-data-lake/dtm
dtm pull gcs-origin
```

---

## 🔌 Integrations

### Apache Airflow
Use `DTMSnapshotOperator` to automatically snapshot data in your DAGs.

```python
from src.integrations.airflow import DTMSnapshotOperator

snapshot_task = DTMSnapshotOperator(
    task_id='snapshot_data',
    message='Post-transformation snapshot',
    repo_path='/data/project'
)
```

### Prefect
Use the `create_dtm_snapshot` task in your flows.

```python
from src.integrations.prefect import create_dtm_snapshot

@flow
def data_pipeline():
    # ... processing ...
    create_dtm_snapshot(message="Pipeline Success", repo_path=".")
```

---

## 🏗️ Project Structure

```
data-time-machine/
├── src/
│   ├── cli.py              # CLI Entry point
│   ├── core/
│   │   ├── backends.py     # Storage Backends (Local, S3, GCS, Azure)
│   │   ├── remote.py       # Remote Manager (Push/Pull)
│   │   ├── storage.py      # Storage Engine & Compression
│   │   └── controller.py   # Business Logic
│   ├── web/                # FastAPI Web Dashboard
│   └── integrations/       # Airflow & Prefect modules
├── scripts/                # Utility scripts
└── README.md
```

---

## 📋 Roadmap (Completed)

- [x] Add diff visualization between snapshots
- [x] Implement remote repository support
- [x] Add compression for large file storage
- [x] Create web-based visualization dashboard
- [x] Support for incremental snapshots
- [x] Integration with popular data pipeline frameworks (Airflow, Prefect)
- [x] Cloud storage backends (S3, GCS, Azure Blob)

---

## 👤 Author

**Azmat Siddique**

- GitHub: [@azmatsiddique](https://github.com/azmatsiddique)
- Project Link: [github.com/azmatsiddique/data-time-machine](https://github.com/azmatsiddique/data-time-machine)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ by [Azmat Siddique](https://github.com/azmatsiddique)

</div>
