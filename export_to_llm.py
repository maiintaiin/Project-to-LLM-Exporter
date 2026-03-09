import os
import tkinter as tk
from tkinter import filedialog

# 擴充忽略資料夾：加入 Visual Studio 常見的編譯與暫存資料夾
IGNORE_DIRS = {
    '.git', '.vscode', '.idea', '__pycache__', 'node_modules', 'venv', 'env', 
    'build', 'dist', 'out', 'x64', 'x86', 'Debug', 'Release', '.vs', 'android', 'ios'
}

# 擴充忽略副檔名：加入 C++ / VS 常見的編譯中間檔與專案設定檔
IGNORE_EXTS = {
    # 圖片與圖示 (Images & Icons)
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico',
    
    # 音效與影音 (Audio & Video)
    '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mkv',
    
    # 3D 模型 (3D Models)
    '.obj', '.fbx', '.glb', '.gltf', '.blend',
    
    # 字體 (Fonts)
    '.ttf', '.otf', '.woff', '.woff2',
    
    # 執行檔、二進位檔與動態連結庫 (Executables & Binaries)
    '.exe', '.dll', '.so', '.bin', '.class', '.pyc', '.o',
    
    # 封裝檔、壓縮檔與安裝檔 (Archives & Packages)
    '.zip', '.tar', '.gz', '.iso', '.dmg', '.pkg', '.app', '.apk', 
    '.aab', '.ipa', '.jar', '.war', '.ear', '.pck',
    
    # 資料庫、大型資料與日誌 (Data, Docs & Logs)
    '.db', '.csv', '.data', '.log', '.pdf',
    
    # C++ / Visual Studio 編譯與設定檔 (C++ / VS Build Files)
    '.lib', '.pdb', '.ilk', '.tlog', '.idb', '.lastbuildstate', 
    '.recipe', '.vcxproj', '.filters', '.user',
    
    # Godot 等遊戲引擎專屬 (Game Engine Specific)
    '.import'
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
    """讀取並格式化檔案內容 (支援多種編碼)"""
    content_str = "## 檔案內容 (File Contents)\n\n"
    
    # 定義要嘗試的編碼順序 (UTF-8, 帶 BOM 的 UTF-8, 繁體中文 Big5)
    encodings_to_try = ['utf-8', 'utf-8-sig', 'big5', 'cp950']
    
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
            
            file_content = None
            
            # 嘗試用不同編碼讀取檔案
            for enc in encodings_to_try:
                try:
                    with open(filepath, 'r', encoding=enc) as file:
                        file_content = file.read()
                    break  # 成功讀取就跳出迴圈
                except UnicodeDecodeError:
                    continue # 失敗就換下一種編碼試試看
            
            if file_content is not None:
                content_str += f"### File: `{rel_path}`\n"
                lang = ext[1:] if ext else "text"
                content_str += f"```{lang}\n{file_content}\n```\n\n"
            else:
                # 所有編碼都失敗，才判定為二進位檔
                content_str += f"### File: `{rel_path}`\n*[Skipped: Binary or unsupported encoding]*\n\n"
                
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
    root = tk.Tk()
    root.withdraw()
    
    print("請在跳出的視窗中選擇你要打包的專案資料夾...")
    target_dir = filedialog.askdirectory(title="選擇要匯出的專案資料夾")
    
    if target_dir:
        folder_name = os.path.basename(os.path.normpath(target_dir))
        output_filename = f"{folder_name}_project_context.md"
        IGNORE_FILES.add(output_filename)
        export_project_for_llm(target_dir, output_filename)
    else:
        print("已取消選擇。")