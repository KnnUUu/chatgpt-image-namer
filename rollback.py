import os

FOLDER = 'D://Pictures//meme//Unnamed'
LOG_PATH = os.path.join(FOLDER, "rename_log.txt")

def rollback_renames(folder, log_path):
    if not os.path.exists(log_path):
        print("No log file found.")
        return

    # 读取所有log行
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if "->" not in line:
            new_lines.append(line)
            continue
        orig, new = [x.strip() for x in line.split("->")]
        orig_path = os.path.join(folder, orig)
        new_path = os.path.join(folder, new)
        # 如果新文件存在且原文件名未被占用，则回滚
        if os.path.exists(new_path):
            if not os.path.exists(orig_path):
                os.rename(new_path, orig_path)
                print(f"Rolled back: {new} -> {orig}")
            else:
                print(f"Cannot rollback {new}: {orig} already exists!")
        else:
            print(f"File not found for rollback: {new}")
        # 不保留已回滚的行

    # 只保留未回滚的行（即未成功回滚的行）
    with open(log_path, "w", encoding="utf-8") as f:
        for line in new_lines:
            f.write(line)

if __name__ == "__main__":
    rollback_renames(FOLDER, LOG_PATH)