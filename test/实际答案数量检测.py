import os
import re

def count_uppercase_letters(file_path):
    
    uppercase_count = 0
    total_lines = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # 跳过空行
                    total_lines += 1
                    # 使用正则表达式匹配所有大写字母
                    uppercase_letters = re.findall(r'[A-Z]', line)
                    uppercase_count += len(uppercase_letters)
                    print(f"第{total_lines}行: '{line}' - 包含 {len(uppercase_letters)} 个大写字母")
    
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return 0
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return 0
    
    return uppercase_count

def main():
    # 获取用户输入的文件路径
    file_path = input("请输入要统计大写字母的文件路径: ")
    
    # 如果用户没有输入路径，使用默认路径
    if not file_path.strip():
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建answers.txt文件的完整路径（在上一级目录）
        file_path = os.path.join(script_dir, "..", "answers.txt")
        print(f"使用默认文件路径: {file_path}")
    
    print(f"正在检查文件: {file_path}")
    print("=" * 50)
    
    # 统计大写字母数量
    total_uppercase = count_uppercase_letters(file_path)
    
    print("=" * 50)
    print(f"文件中的大写英文字母总数: {total_uppercase}")

if __name__ == "__main__":
    main()