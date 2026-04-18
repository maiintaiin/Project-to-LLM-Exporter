import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

# ==========================================
# 1. 擋下深淵：資料夾黑名單 (避免浪費時間遍歷)
# ==========================================
IGNORE_DIRS = {
    # 共同環境
    '.git', '.vscode', '.idea', '.vs', '__pycache__', 'venv', 'env', 'node_modules',
    # C++ / 輸出
    'build', 'dist', 'out', 'x64', 'x86', 'Debug', 'Release',
    # 遊戲引擎
    '.godot', '.import', 'export', 'Library', 'Temp', 'Logs', 'obj', 'Builds'
}

# ==========================================
# 2. 迎向光明：副檔名白名單 (只允許這些檔案通過)
# ==========================================
ALLOWED_EXTS = {
    # 網頁前端 (Web)
    '.html', '.htm', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
    # 後端與腳本 (Backend & Scripts)
    '.py', '.java', '.go', '.rb', '.php', '.sh', '.bat', '.ps1',
    # C / C++ / C#
    '.c', '.cpp', '.h', '.hpp', '.cc', '.cs',
    # 遊戲引擎專屬 (Godot & Unity)
    '.gd', '.tscn', '.tres', '.gdshader', '.shader', '.cginc', '.hlsl', '.glsl',
    # 設定檔、文件與純文字資料 (Config & Text)
    '.md', '.txt', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf', '.env'
}

# ==========================================
# 3. 特殊通行證：允許無副檔名或特定名稱的檔案
# ==========================================
ALLOWED_FILENAMES = {
    'Makefile', 'Dockerfile', 'CMakeLists.txt', 'requirements.txt', '.gitignore'
}

IGNORE_FILES = set()

# ==========================================
# 核心邏輯
# ==========================================

def is_file_allowed(filename):
    """判斷檔案是否在白名單內"""
    if filename in IGNORE_FILES:
        return False
        
    if filename in ALLOWED_FILENAMES:
        return True
        
    ext = os.path.splitext(filename)[1].lower()
    if ext in ALLOWED_EXTS:
        return True
        
    return False

def count_valid_files(startpath):
    total_files = 0
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if is_file_allowed(f):
                total_files += 1
    return total_files

def generate_directory_tree(startpath):
    tree_str = "## 專案目錄結構 (Directory Structure)\n```text\n"
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        basename = os.path.basename(root)
        
        if basename:
            tree_str += f"{indent}{basename}/\n"
        else:
            tree_str += f"root/\n"
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if is_file_allowed(f):
                tree_str += f"{subindent}{f}\n"
    tree_str += "```\n\n"
    return tree_str

def export_project_with_progress(project_dir, output_file, root_window):
    progress_win = tk.Toplevel(root_window)
    progress_win.title("打包進度 (白名單模式)")
    progress_win.geometry("450x150")
    progress_win.geometry(f"+{progress_win.winfo_screenwidth()//2 - 225}+{progress_win.winfo_screenheight()//2 - 75}")
    progress_win.resizable(False, False)
    progress_win.attributes('-topmost', True) 

    lbl_status = tk.Label(progress_win, text="正在計算檔案數量...", font=("微軟正黑體", 10))
    lbl_status.pack(pady=(15, 5))

    progress_bar = ttk.Progressbar(progress_win, orient="horizontal", length=380, mode="determinate")
    progress_bar.pack(pady=5)

    lbl_file = tk.Label(progress_win, text="", font=("微軟正黑體", 8), fg="gray")
    lbl_file.pack(pady=5)
    
    progress_win.update()

    total_files = count_valid_files(project_dir)
    if total_files == 0:
        messagebox.showinfo("提示", "找不到任何符合白名單的程式碼檔案！\n請檢查 ALLOWED_EXTS 設定。")
        progress_win.destroy()
        return

    progress_bar["maximum"] = total_files
    
    lbl_status.config(text="正在生成目錄結構樹...")
    progress_win.update()
    tree_str = generate_directory_tree(project_dir)
    
    lbl_status.config(text=f"正在處理檔案 (0/{total_files})...")
    content_str = "## 檔案內容 (File Contents)\n\n"
    encodings_to_try = ['utf-8', 'utf-8-sig', 'big5', 'cp950']
    
    processed_count = 0

    for root_dir, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for f in files:
            if not is_file_allowed(f):
                continue
            
            filepath = os.path.join(root_dir, f)
            rel_path = os.path.relpath(filepath, project_dir)
            ext = os.path.splitext(f)[1].lower()
            
            processed_count += 1
            progress_bar["value"] = processed_count
            lbl_status.config(text=f"正在處理檔案 ({processed_count}/{total_files}) - {int((processed_count/total_files)*100)}%")
            display_path = rel_path if len(rel_path) < 50 else "..." + rel_path[-47:]
            lbl_file.config(text=display_path)
            progress_win.update()
            
            file_content = None
            for enc in encodings_to_try:
                try:
                    with open(filepath, 'r', encoding=enc) as file:
                        file_content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if file_content is not None:
                content_str += f"### File: `{rel_path}`\n"
                lang = ext[1:] if ext else "text"
                if lang == "gd": lang = "gdscript" 
                content_str += f"```{lang}\n{file_content}\n```\n\n"
            else:
                content_str += f"### File: `{rel_path}`\n*[Skipped: Unsupported encoding]*\n\n"

    lbl_status.config(text="正在寫入 Markdown 檔案...")
    lbl_file.config(text="")
    progress_win.update()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 專案程式碼匯出 ({os.path.basename(project_dir)})\n\n")
        f.write(tree_str)
        f.write(content_str)
        
    progress_win.destroy()
    messagebox.showinfo("匯出完成！", f"成功打包了 {total_files} 個檔案。\n採用「白名單模式」，輸出純淨度 100%。\n檔案已儲存至：\n{os.path.abspath(output_file)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    target_dir = filedialog.askdirectory(title="選擇要匯出的專案資料夾")
    
    if target_dir:
        folder_name = os.path.basename(os.path.normpath(target_dir))
        output_filename = f"{folder_name}_project_context.md"
        IGNORE_FILES.add(output_filename)
        
        export_project_with_progress(target_dir, output_filename, root)
    
    root.destroy()