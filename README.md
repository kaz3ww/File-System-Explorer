# File-System-Explorer
A GUI-based File System Explorer built with Python (Tkinter). Features include creating, deleting, renaming files/folders, viewing details, and managing permissions. Also includes a Storage Allocation Simulator using the First-Fit strategy to demonstrate memory management.

It is designed as an **educational tool** for learning about file systems and memory allocation in Operating Systems.

---

## ✨ Features
- 📂 **File Explorer**
  - Create, delete, rename files & directories
  - View details: size, timestamps, contents
  - Show & modify permissions (Read/Write/Execute)

- 💾 **Storage Allocator**
  - Allocate & deallocate blocks using **First-Fit**
  - Display allocation map visually

- 🎨 **User Interface**
  - Modern themed UI
  - Emoji-based icons for better visualization

---

## 📂 Project Structure


---

## ⚙️ Installation

1. **Clone this repository**  
```bash
git clone https://github.com/kaz3ww/file-system-explorer.git
cd file-system-explorer

python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

pip install -r requirements.txt

python main.py

class StorageAllocator:
    def __init__(self, size=100):
        self.size = size
        self.blocks = [0] * size

    def first_fit_allocate(self, size):
        start = -1
        free_blocks = 0
        for i in range(len(self.blocks)):
            if self.blocks[i] == 0:
                if free_blocks == 0:
                    start = i
                free_blocks += 1
                if free_blocks == size:
                    for j in range(start, start + size):
                        self.blocks[j] = 1
                    return start
            else:
                free_blocks = 0
                start = -1
        return -1
