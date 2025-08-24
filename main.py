import os
import shutil
import stat
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

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

    def deallocate(self, start, size):
        for i in range(start, start + size):
            if i < len(self.blocks):
                self.blocks[i] = 0

    def get_allocation_map(self):
        return "".join(['X' if x else '.' for x in self.blocks])

class FileSystemExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 File System Explorer")
        self.storage = StorageAllocator(100)
        
        # Set window icon
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # ===== Color Theme =====
        self.colors = {
            'primary': '#2E3440',
            'secondary': '#3B4252',
            'accent': '#81A1C1',
            'text': '#ECEFF4',
            'text_secondary': '#D8DEE9',
            'success': '#A3BE8C',
            'warning': '#EBCB8B',
            'error': '#BF616A',
            'highlight': '#5E81AC',
            'background': '#1E222A'
        }

        # ===== Styling =====
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('.', 
                           background=self.colors['background'],
                           foreground=self.colors['text'])
        
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('TNotebook', background=self.colors['primary'])
        self.style.configure('TNotebook.Tab', 
                           background=self.colors['secondary'],
                           foreground=self.colors['text'],
                           padding=[10, 5])
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.colors['primary'])],
                      foreground=[('selected', self.colors['accent'])])
        
        self.style.configure('TLabel', 
                           background=self.colors['background'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        
        self.style.configure('TButton',
                           background=self.colors['secondary'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=8,
                           borderwidth=1)
        self.style.map('TButton',
                      background=[('active', self.colors['highlight']),
                                 ('pressed', self.colors['accent'])],
                      foreground=[('active', 'white')])
        
        self.style.configure('Treeview',
                           background=self.colors['secondary'],
                           foreground=self.colors['text'],
                           fieldbackground=self.colors['secondary'],
                           font=('Segoe UI', 10))
        self.style.map('Treeview',
                      background=[('selected', self.colors['highlight'])],
                      foreground=[('selected', 'white')])
        
        self.style.configure('Treeview.Heading',
                           background=self.colors['primary'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('TLabelframe',
                           background=self.colors['background'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 10, 'bold'))
        self.style.configure('TLabelframe.Label',
                           background=self.colors['background'],
                           foreground=self.colors['accent'])
        
        # Configure text widget
        self.text_bg = self.colors['secondary']
        self.text_fg = self.colors['text']

        # ===== Load Icons =====
        self.icons = {
            'folder': self.create_icon('#81A1C1', '📁'),
            'file': self.create_icon('#D8DEE9', '📄'),
            'create_file': self.create_icon('#A3BE8C', '📄'),
            'create_dir': self.create_icon('#A3BE8C', '📁'),
            'delete': self.create_icon('#BF616A', '🗑️'),
            'rename': self.create_icon('#EBCB8B', '✏️'),
            'details': self.create_icon('#81A1C1', '🔎'),
            'permissions': self.create_icon('#B48EAD', '🔐'),
            'modify_perms': self.create_icon('#B48EAD', '🛠️'),
            'allocate': self.create_icon('#8FBCBB', '➕'),
            'deallocate': self.create_icon('#D08770', '➖'),
            'storage_map': self.create_icon('#81A1C1', '🗺️')
        }

        # ===== Main Layout =====
        self.root.configure(background=self.colors['background'])
        
        # Setup notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.explorer_tab = ttk.Frame(self.notebook)
        self.storage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.explorer_tab, text="📂 File Explorer")
        self.notebook.add(self.storage_tab, text="💾 Storage Allocator")

        # === File Explorer Tab ===
        self.explorer_tab.columnconfigure(0, weight=3)
        self.explorer_tab.columnconfigure(1, weight=1)
        self.explorer_tab.rowconfigure(0, weight=1)

        # Treeview with scrollbar
        tree_frame = ttk.Frame(self.explorer_tab)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewOpen>>', self.on_open)

        scroll = ttk.Scrollbar(tree_frame, command=self.tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scroll.set)

        root_path = os.path.abspath('.')
        root_node = self.tree.insert('', 'end', text=root_path, open=True, 
                                   image=self.icons['folder'], values=[root_path])
        self.populate_tree(root_node, root_path)

        # Actions Panel
        ops_frame = ttk.LabelFrame(self.explorer_tab, text="🛠️ File Operations")
        ops_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        ops_frame.columnconfigure(0, weight=1)
        
        buttons = [
            ("Create File", self.create_file, 'create_file'),
            ("Create Directory", self.create_dir, 'create_dir'),
            ("Delete", self.delete_item, 'delete'),
            ("Rename", self.rename_item, 'rename'),
            ("Show Details", self.show_details, 'details'),
            ("Show Permissions", self.show_permissions, 'permissions'),
            ("Modify Permissions", self.modify_permissions, 'modify_perms')
        ]
        
        for row, (text, cmd, icon) in enumerate(buttons):
            btn = ttk.Button(ops_frame, text=text, command=cmd, 
                            image=self.icons[icon], compound=tk.LEFT)
            btn.grid(row=row, column=0, sticky="ew", padx=5, pady=4)
            ops_frame.rowconfigure(row, weight=1)

        # === Storage Tab ===
        self.storage_tab.columnconfigure(0, weight=1)
        self.storage_tab.rowconfigure(1, weight=1)

        # Header
        header = ttk.Frame(self.storage_tab)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        ttk.Label(header, text="💾 Storage Allocation (First Fit)", 
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(self.storage_tab)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        for i in range(3): btn_frame.columnconfigure(i, weight=1)

        ttk.Button(btn_frame, text="Allocate Blocks", command=self.allocate_blocks,
                  image=self.icons['allocate'], compound=tk.LEFT).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(btn_frame, text="Deallocate Blocks", command=self.deallocate_blocks,
                  image=self.icons['deallocate'], compound=tk.LEFT).grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(btn_frame, text="Show Allocation Map", command=self.show_storage_map,
                  image=self.icons['storage_map'], compound=tk.LEFT).grid(row=0, column=2, padx=5, sticky="ew")

        # Text output for storage map
        output_frame = ttk.Frame(self.storage_tab)
        output_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.storage_output = tk.Text(output_frame, height=10, font=("Consolas", 11), 
                                     wrap=tk.NONE, bg=self.text_bg, fg=self.text_fg,
                                     insertbackground=self.colors['text'],
                                     selectbackground=self.colors['highlight'])
        self.storage_output.grid(row=0, column=0, sticky="nsew")

        text_scroll = ttk.Scrollbar(output_frame, command=self.storage_output.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        self.storage_output.config(yscrollcommand=text_scroll.set)

        # Configure root window resizing
        root.minsize(800, 600)
        root.geometry("1000x650")
        
    def create_icon(self, color, emoji=None):
        """Create a more sophisticated icon with emoji overlay"""
        icon = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Draw background circle
        draw.ellipse([2, 2, 22, 22], fill=color)
        
        # Add emoji if provided
        if emoji:
            try:
                font = ImageFont.truetype("seguiemj.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Get text bounding box using textbbox (replaces deprecated textsize)
            bbox = draw.textbbox((0, 0), emoji, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((24-w)/2, (24-h)/2-2), emoji, font=font, embedded_color=True)
        
        return ImageTk.PhotoImage(icon)

    def populate_tree(self, parent, path):
        self.tree.delete(*self.tree.get_children(parent))
        try:
            for item in sorted(os.listdir(path), key=lambda x: x.lower()):
                full_path = os.path.join(path, item)
                img = self.icons['folder'] if os.path.isdir(full_path) else self.icons['file']
                node = self.tree.insert(parent, 'end', text=item, image=img, values=[full_path])
                if os.path.isdir(full_path):
                    self.tree.insert(node, 'end')  # dummy child
        except Exception as e:
            pass

    def on_open(self, event):
        node = self.tree.focus()
        path = self.tree.item(node)['values'][0]
        self.populate_tree(node, path)

    def get_selected_path(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a file or folder first.")
            return None
        return self.tree.item(selected)['values'][0]

    # === File Operations ===
    def create_file(self):
        path = self.get_selected_path()
        if path and os.path.isdir(path):
            name = simpledialog.askstring("Create File", "Enter file name:", parent=self.root)
            if name:
                try:
                    open(os.path.join(path, name), 'w').close()
                    self.populate_tree(self.tree.focus(), path)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self.root)

    def create_dir(self):
        path = self.get_selected_path()
        if path and os.path.isdir(path):
            name = simpledialog.askstring("Create Directory", "Enter directory name:", parent=self.root)
            if name:
                try:
                    os.mkdir(os.path.join(path, name))
                    self.populate_tree(self.tree.focus(), path)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self.root)

    def delete_item(self):
        path = self.get_selected_path()
        if path:
            confirm = messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete:\n{path}?",
                                        parent=self.root)
            if confirm:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    parent = self.tree.parent(self.tree.focus())
                    parent_path = self.tree.item(parent)['values'][0]
                    self.populate_tree(parent, parent_path)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self.root)

    def rename_item(self):
        path = self.get_selected_path()
        if path:
            new_name = simpledialog.askstring("Rename", "Enter new name:", parent=self.root)
            if new_name:
                new_path = os.path.join(os.path.dirname(path), new_name)
                try:
                    os.rename(path, new_path)
                    parent = self.tree.parent(self.tree.focus())
                    parent_path = self.tree.item(parent)['values'][0]
                    self.populate_tree(parent, parent_path)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self.root)

    def show_details(self):
        path = self.get_selected_path()
        if path:
            try:
                if os.path.isfile(path):
                    size = os.path.getsize(path)
                    mod_time = os.path.getmtime(path)
                    created_time = os.path.getctime(path)
                    formatted_mod = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    formatted_created = datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
                    messagebox.showinfo("File Details", 
                                      f"Path: {path}\nSize: {size:,} bytes\n"
                                      f"Created: {formatted_created}\n"
                                      f"Modified: {formatted_mod}", parent=self.root)
                elif os.path.isdir(path):
                    num_files = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
                    num_dirs = len([name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))])
                    mod_time = os.path.getmtime(path)
                    formatted_mod = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
                    messagebox.showinfo("Directory Details", 
                                      f"Path: {path}\n"
                                      f"Contents: {num_files} files, {num_dirs} subdirectories\n"
                                      f"Modified: {formatted_mod}", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self.root)

    def show_permissions(self):
        path = self.get_selected_path()
        if path:
            try:
                stat_info = os.stat(path)
                mode = stat_info.st_mode
                perms = {
                    'Owner': {
                        'Read': bool(mode & stat.S_IRUSR),
                        'Write': bool(mode & stat.S_IWUSR),
                        'Execute': bool(mode & stat.S_IXUSR)
                    },
                    'Group': {
                        'Read': bool(mode & stat.S_IRGRP),
                        'Write': bool(mode & stat.S_IWGRP),
                        'Execute': bool(mode & stat.S_IXGRP)
                    },
                    'Others': {
                        'Read': bool(mode & stat.S_IROTH),
                        'Write': bool(mode & stat.S_IWOTH),
                        'Execute': bool(mode & stat.S_IXOTH)
                    }
                }
                
                permission_str = "🔐 Permissions:\n\n"
                for category, rights in perms.items():
                    permission_str += f"{category}:\n"
                    for right, value in rights.items():
                        permission_str += f"  {right}: {'✅' if value else '❌'}\n"
                    permission_str += "\n"
                
                messagebox.showinfo("Permissions", permission_str, parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=self.root)

    def modify_permissions(self):
        path = self.get_selected_path()
        if path:
            options = {
                '1': ("Read Only", stat.S_IRUSR),
                '2': ("Write Only", stat.S_IWUSR),
                '3': ("Execute Only", stat.S_IXUSR),
                '4': ("Read + Write", stat.S_IRUSR | stat.S_IWUSR),
                '5': ("Read + Execute", stat.S_IRUSR | stat.S_IXUSR),
                '6': ("Full Control", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            }
            
            choice = simpledialog.askstring("Modify Permissions", 
                                          "Choose permission level:\n\n"
                                          "1. Read Only\n"
                                          "2. Write Only\n"
                                          "3. Execute Only\n"
                                          "4. Read + Write\n"
                                          "5. Read + Execute\n"
                                          "6. Full Control",
                                          parent=self.root)
            
            if choice in options:
                try:
                    os.chmod(path, options[choice][1])
                    messagebox.showinfo("Success", 
                                      f"Permissions set to: {options[choice][0]}", 
                                      parent=self.root)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self.root)

    # === Storage Functions ===
    def allocate_blocks(self):
        size = simpledialog.askinteger("Allocate Blocks", 
                                     "Number of blocks to allocate:",
                                     minvalue=1, maxvalue=self.storage.size,
                                     parent=self.root)
        if size:
            start = self.storage.first_fit_allocate(size)
            if start != -1:
                self.storage_output.insert('end', f"✅ Allocated blocks {start} to {start + size - 1}\n")
                self.storage_output.tag_config('success', foreground=self.colors['success'])
                self.storage_output.tag_add('success', 'end-1l linestart', 'end-1l lineend')
            else:
                messagebox.showerror("Error", "Not enough contiguous free blocks.", parent=self.root)

    def deallocate_blocks(self):
        start = simpledialog.askinteger("Deallocate Blocks", 
                                      "Starting block number:",
                                      minvalue=0, maxvalue=self.storage.size-1,
                                      parent=self.root)
        if start is not None:
            size = simpledialog.askinteger("Deallocate Blocks", 
                                          "Number of blocks to deallocate:",
                                          minvalue=1, maxvalue=self.storage.size-start,
                                          parent=self.root)
            if size is not None:
                self.storage.deallocate(start, size)
                self.storage_output.insert('end', f"🗑️ Deallocated blocks {start} to {start + size - 1}\n")
                self.storage_output.tag_config('warning', foreground=self.colors['warning'])
                self.storage_output.tag_add('warning', 'end-1l linestart', 'end-1l lineend')

    def show_storage_map(self):
        self.storage_output.insert('end', "\n📊 Storage Allocation Map:\n")
        self.storage_output.tag_config('header', foreground=self.colors['accent'])
        self.storage_output.tag_add('header', 'end-1l linestart', 'end-1l lineend')
        
        map_str = self.storage.get_allocation_map()
        formatted = '\n'.join([f"{i*20:3d}: {map_str[i*20:(i+1)*20]}" 
                             for i in range(0, (len(map_str)+19)//20)])
        
        self.storage_output.insert('end', formatted + '\n\n')
        self.storage_output.see("end")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemExplorerApp(root)
    root.mainloop()