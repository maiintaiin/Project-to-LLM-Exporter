import os
import tkinter as tk
from tkinter import filedialog

# 預設要忽略的資料夾
IGNORE_DIRS = {'.git', '.vscode', '.idea', '__pycache__', 'node_modules', 'venv', 'env', 'build', 'dist', 'out'}

# 擴充後的忽略副檔名清單 
IGNORE_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.exe', '.dll', '.pdf', '.zip', '.tar', '.gz', 
    '.pyc', '.class', '.o', '.so', '.db', '.csv', '.data', '.log', '.bin', '.mp4', 
    '.mp3', '.avi', '.mkv', '.iso', '.dmg', '.pkg', '.app', '.apk', '.jar', '.war', '.ear'
}

# 預設忽略的檔案集合
IGNORE_FILES = set() 

def generate_directory_tree(startpath):
    """生成目錄結構樹"""
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
            if f in IGNORE_FILES:
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext not in IGNORE_EXTS:
                tree_str += f"{subindent}{f}\n"
    tree_str += "```\n\n"
    return tree_str

def generate_file_contents(startpath):
    """讀取並格式化檔案內容"""
    content_str = "## 檔案內容 (File Contents)\n\n"
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for f in files:
            if f in IGNORE_FILES:
                continue
                
            ext = os.path.splitext(f)[1].lower()
            if ext in IGNORE_EXTS:
                continue
            
            filepath = os.path.join(root, f)
            rel_path = os.path.relpath(filepath, startpath)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    file_content = file.read()
                    
                content_str += f"### File: `{rel_path}`\n"
                lang = ext[1:] if ext else "text"
                content_str += f"```{lang}\n{file_content}\n```\n\n"
            except UnicodeDecodeError:
                content_str += f"### File: `{rel_path}`\n*[Skipped: Binary or non-UTF-8 file]*\n\n"
            except Exception as e:
                content_str += f"### File: `{rel_path}`\n*[Error reading file: {e}]*\n\n"
                
    return content_str

def export_project_for_llm(project_dir, output_file):
    print(f"開始掃描目錄: {project_dir}")
    tree = generate_directory_tree(project_dir)
    contents = generate_file_contents(project_dir)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 專案程式碼匯出 ({os.path.basename(project_dir)})\n\n")
        f.write(tree)
        f.write(contents)
        
    print(f"輸出完成！檔案已儲存至: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # 初始化 tkinter 並隱藏主視窗
    root = tk.Tk()
    root.withdraw()
    
    print("請在跳出的視窗中選擇你要打包的專案資料夾...")
    
    # 開啟選擇目錄的對話框
    target_dir = filedialog.askdirectory(title="選擇要匯出的專案資料夾")
    
    if target_dir:
        # 取得選擇的資料夾名稱 (使用 normpath 確保路徑格式正確再取 basename)
        folder_name = os.path.basename(os.path.normpath(target_dir))
        
        # 組合新的檔名，例如：SimpleDPSystem_project_context.md
        output_filename = f"{folder_name}_project_context.md"
        
        # 將動態產生的檔名加入忽略清單
        IGNORE_FILES.add(output_filename)
        
        export_project_for_llm(target_dir, output_filename)
    else:
        print("已取消選擇。")