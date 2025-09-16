import os
import re
from bs4 import BeautifulSoup

class HtmlToTextConverter:
    def __init__(self, html_dir, output_dir):
        """
        初始化HTML到TXT转换器
        
        参数:
            html_dir: HTML文件所在目录
            output_dir: 输出TXT文件的目录
        """
        self.html_dir = html_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def extract_question_and_options(self, html_content):
        """
        从HTML内容中提取题目和选项，支持一个HTML文件中包含多个题目
        
        参数:
            html_content: HTML内容字符串
            
        返回:
            包含题目和选项的字符串
        """
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 检查是否是多个题目的页面（A3/A4题型）
        gong_element = soup.select_one("div.gong")
        shared_stem = ""
        if gong_element:
            # 提取共用题干
            stem_font = gong_element.select_one("font")
            if stem_font:
                shared_stem = stem_font.get_text(strip=True)
        
        # 查找所有题目
        questions = []
        question_items = soup.select("div.question-item")
        
        if not question_items:
            # 如果没有找到question-item，尝试单个题目的结构
            question_items = [soup.select_one("div.test")]
        
        for i, question_item in enumerate(question_items):
            if not question_item:
                continue
                
            # 提取题目
            question_element = question_item.select_one("h2.fch2 font")
            if question_element:
                question_text = question_element.get_text(strip=True)
            else:
                # 备用选择器
                question_element = question_item.select_one("h2.fch2")
                if question_element:
                    question_text = question_element.get_text(strip=True)
                    # 清理题目编号
                    question_text = re.sub(r'^\d+\.\s*', '', question_text)
                else:
                    question_text = "未找到题目"
            
            # 如果有共用题干，添加到题目文本中
            if shared_stem and i == 0:
                question_text = f"【共用题干】{shared_stem}\n{question_text}"
            
            # 提取选项
            options = []
            option_elements = question_item.select("div.selet ul li label.el-radio")
            
            if option_elements:
                for option_element in option_elements:
                    option_value = option_element.select_one("input.el-radio__original").get("value", "")
                    option_text = option_element.select_one("span.el-radio__label font").get_text(strip=True)
                    # 检查选项文本是否已经包含选项字母，避免重复
                    if option_text.startswith(f"{option_value}."):
                        options.append(option_text)
                    else:
                        options.append(f"{option_value}. {option_text}")
            else:
                # 备用选择器
                option_elements = question_item.select("div.selet ul li label")
                if option_elements:
                    for option_element in option_elements:
                        option_text = option_element.get_text(strip=True)
                        if option_text and re.match(r'^[A-E]\.', option_text):
                            options.append(option_text)
            
            questions.append({
                "question": question_text,
                "options": options
            })
        
        # 构建结果字符串
        results = []
        for i, q in enumerate(questions):
            result = f"题目: {q['question']}\n"
            
            if q['options']:
                result += "选项:\n"
                for option in q['options']:
                    result += f"{option}\n"
            else:
                result += "未找到选项\n"
            
            results.append(result)
        
        return "\n".join(results)
    
    def convert_all_html_to_txt(self):
        """
        将所有HTML文件转换为单个TXT文件
        """
        # 获取所有HTML文件
        html_files = [f for f in os.listdir(self.html_dir) if f.endswith('.html')]
        html_files.sort(key=lambda x: int(re.search(r'第(\d+)题\.html', x).group(1)))  # 按题号排序
        
        if not html_files:
            print(f"在目录 {self.html_dir} 中没有找到HTML文件")
            return False
        
        print(f"找到 {len(html_files)} 个HTML文件")

        # 创建单个输出文件
        output_file = os.path.join(self.output_dir, "questions.txt")
        
        # 转换每个HTML文件并追加到输出文件
        for i, html_file in enumerate(html_files):
            print(f"正在处理: {html_file}")
            
            # 构建文件路径
            html_path = os.path.join(self.html_dir, html_file)
            
            # 读取HTML文件
            with open(html_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # 提取题目和选项
            text_content = self.extract_question_and_options(html_content)
            
            # 提取题号
            match = re.search(r'第(\d+)题\.html', html_file)
            question_number = match.group(1) if match else "未知"
            
            # 检查是否是包含多个题目的文件
            soup = BeautifulSoup(html_content, 'html.parser')
            question_items = soup.select("div.question-item")
            if len(question_items) > 1:
                # 如果是多个题目的文件，修改题号表示方式
                first_question = question_items[0].select_one("h2.fch2")
                if first_question:
                    first_num = re.search(r'(\d+)\.', first_question.get_text(strip=True))
                    if first_num:
                        first_num = first_num.group(1)
                        last_question = question_items[-1].select_one("h2.fch2")
                        if last_question:
                            last_num = re.search(r'(\d+)\.', last_question.get_text(strip=True))
                            if last_num:
                                last_num = last_num.group(1)
                                question_number = f"{first_num}-{last_num}"
            
            # 写入到输出文件（第一个文件使用写入模式，后续文件使用追加模式）
            with open(output_file, 'w' if i == 0 else 'a', encoding='utf-8') as f:
                f.write(f"题号: {question_number}\n")
                f.write(text_content)
                f.write("\n" + "-"*20 + "\n\n")
            
            print(f"已处理: {html_file}")
        
        print(f"\n转换完成，共转换 {len(html_files)} 个文件")
        print(f"所有题目已保存到: {output_file}")
        return True

def main():
    # 设置目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_dir = os.path.join(script_dir, "captured_html")
    output_dir = script_dir  # 输出目录为脚本同路径
    
    # 创建转换器实例
    converter = HtmlToTextConverter(html_dir, output_dir)
    
    # 转换所有HTML文件
    converter.convert_all_html_to_txt()

if __name__ == "__main__":
    main()