import os

def count_python_lines(directory):
    total_lines = 0
    pyfiles = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                pyfiles += 1
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except (UnicodeDecodeError, FileNotFoundError):
                    print(f"⚠️ Skipped unreadable file: {filepath}")
    print(f"Total number of python file : {pyfiles}")
    return total_lines

if __name__ == "__main__":
    project_dir = "."  # Change this if your script isn't in the root
    lines = count_python_lines(project_dir)
    print(f"📊 Total lines of Python code: {lines}")