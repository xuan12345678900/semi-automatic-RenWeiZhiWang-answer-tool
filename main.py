#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException
from bs4 import BeautifulSoup

class ExamToolSuite:
    def __init__(self, driver_path=None, exam_url=None):
        """
        初始化考试工具套件
        
        参数:
            driver_path: chromedriver.exe的路径
            exam_url: 考试页面URL
        """
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.driver_path = driver_path or os.path.join(script_dir, "chromedriver-win64", "chromedriver.exe")
        self.exam_url = exam_url or "https://exam.ipmph.com/front/myschool/index.html#/login?Referer=https%3A%2F%2Fexam.ipmph.com%2Fexamzcms%2F"
        self.driver = None
        self.wait = None
        self.answered_questions = set()
        self.current_question = 1
        self.total_questions = 100
        
        # 设置HTML文件相关路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.captured_html_dir = os.path.join(script_dir, "captured_html")
        self.questions_txt_path = os.path.join(script_dir, "questions.txt")
        self.answers_txt_path = os.path.join(script_dir, "answers.txt")
        
        # 确保目录存在
        if not os.path.exists(self.captured_html_dir):
            os.makedirs(self.captured_html_dir)
        
        # 初始化时直接打开浏览器到考试登录页
        self.initialize_browser()
        self.open_exam_page()
    
    def initialize_browser(self):
        """初始化浏览器"""
        if self.driver is not None:
            print("浏览器已经初始化")
            return True
            
        print("正在初始化浏览器...")
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 添加更多选项来解决可能的冲突问题
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-field-trial-config")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # 创建带有时间戳的唯一临时用户数据目录，避免Chrome用户数据目录冲突
        import uuid
        temp_dir = os.path.join(tempfile.gettempdir(), f"chrome_user_data_{uuid.uuid4().hex}")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # 保存临时目录路径，以便后续清理
        self.temp_user_data_dir = temp_dir
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
        print("浏览器初始化完成")
        return True
    
    def wait_for_page_load(self, timeout=30):
        """
        等待页面加载完成，每0.3秒检查一次
        
        参数:
            timeout: 最大等待时间（秒）
            
        返回:
            是否成功加载
        """
        print("等待页面加载...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查页面是否加载完成
            if self.driver.execute_script("return document.readyState") == "complete":
                print("页面加载完成")
                return True
            
            # 每0.3秒检查一次
            time.sleep(0.3)
        
        print(f"页面加载超时（{timeout}秒）")
        return False
    
    def open_exam_page(self):
        """
        打开考试页面
        """
        if not self.initialize_browser():
            return False
            
        print(f"正在打开考试页面: {self.exam_url}")
        self.driver.get(self.exam_url)
        
        # 等待页面加载
        if not self.wait_for_page_load():
            print("页面加载失败")
            return False
        
        print("页面加载成功")
        print("请手动登录并导航到考试页面，准备好后请按Enter键继续...")
        input()
        
        return True
    
    def get_current_question_number(self):
        """
        获取当前题号
        
        返回:
            当前题号，如果无法获取则返回0
        """
        try:
            # 尝试从页面标题中获取题号
            title_element = self.driver.find_element(By.CSS_SELECTOR, ".h4.fch2")
            title_text = title_element.text
            # 使用正则表达式提取题号，例如 "150.【A2 题型】" 中的 "150"
            match = re.search(r'(\d+)\.', title_text)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"从标题获取题号失败: {e}")
        
        try:
            # 尝试从进度条中获取当前题号
            progress_text = self.driver.find_element(By.CSS_SELECTOR, ".el-progress__text").text
            # 例如 "4%"，我们需要计算当前题号
            progress_percent = int(progress_text.replace('%', ''))
            # 从总题数计算当前题号
            total_questions = self.get_total_questions()
            if total_questions > 0:
                current_question = round(total_questions * progress_percent / 100)
                return max(1, current_question)  # 至少返回1
        except Exception as e:
            print(f"从进度条获取题号失败: {e}")
        
        return self.current_question
    
    def get_total_questions(self):
        """
        获取总题数
        
        返回:
            总题数，如果无法获取则返回0
        """
        try:
            # 尝试从进度条上方获取总题数
            progress_text = self.driver.find_element(By.XPATH, "//span[contains(text(), '共') and contains(text(), '道题')]").text
            # 使用正则表达式提取总题数，例如 "共150道题" 中的 "150"
            match = re.search(r'共(\d+)道题', progress_text)
            if match:
                return int(match.group(1))
        except Exception as e:
            print(f"从进度条上方获取总题数失败: {e}")
        
        try:
            # 尝试从剩余题数中获取总题数
            remaining_text = self.driver.find_element(By.CSS_SELECTOR, ".red").text
            # 使用正则表达式提取剩余题数，例如 "150道" 中的 "150"
            match = re.search(r'(\d+)道', remaining_text)
            if match:
                remaining = int(match.group(1))
                # 如果能获取到当前题号，可以计算总题数
                current = self.get_current_question_number()
                if current > 0:
                    return current + remaining
        except Exception as e:
            print(f"从剩余题数获取总题数失败: {e}")
        
        return self.total_questions
    
    def clear_captured_html_folder(self):
        """
        清空captured_html文件夹中的所有HTML文件
        """
        try:
            # 检查目录是否存在
            if not os.path.exists(self.captured_html_dir):
                print(f"目录 {self.captured_html_dir} 不存在，无需清空")
                return True
            
            # 获取目录中的所有文件
            files = os.listdir(self.captured_html_dir)
            
            # 如果目录为空，无需操作
            if not files:
                print(f"目录 {self.captured_html_dir} 已经为空")
                return True
            
            # 删除所有HTML文件
            deleted_count = 0
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(self.captured_html_dir, file)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"已删除: {file_path}")
                    except Exception as e:
                        print(f"删除文件 {file_path} 时出错: {e}")
            
            print(f"清空操作完成，共删除 {deleted_count} 个HTML文件")
            return True
            
        except Exception as e:
            print(f"清空captured_html文件夹时出错: {e}")
            return False

    def capture_all_questions(self):
        """
        捕获所有题目的HTML
        """
        # 首先清空captured_html文件夹
        print("正在清空captured_html文件夹...")
        if not self.clear_captured_html_folder():
            print("清空captured_html文件夹失败，继续执行捕获操作")
        
        # 确保浏览器已打开
        if not self.driver:
            print("浏览器未打开，正在重新打开...")
            if not self.open_exam_page():
                print("无法打开考试页面")
                return False
        
        # 获取总题数
        print("正在获取总题数...")
        total_questions = self.get_total_questions()
        if total_questions > 0:
            print(f"检测到总题数: {total_questions}")
            self.total_questions = total_questions
        else:
            print("无法检测到总题数，将使用默认最大题目数量")
            total_questions = 200  # 默认最大题目数量
        
        # 初始化计数器
        question_count = 0
        max_questions = total_questions + 50  # 设置最大题目数量为总题数+50，确保能捕获所有题目
        
        # 记录已经捕获的题号，避免重复
        captured_questions = set()
        
        print(f"开始捕获题目，预计最多捕获 {max_questions} 题...")
        
        # 循环捕获每一题
        while question_count < max_questions:
            print(f"\n=== 处理第 {question_count + 1} 题 ===")
            
            # 获取当前题号
            print("正在获取当前题号...")
            current_question = self.get_current_question_number()
            print(f"当前题号: {current_question}")
            
            # 如果无法获取当前题号，使用计数器
            if current_question == 0:
                current_question = question_count + 1
                print(f"无法获取题号，使用计数器值: {current_question}")
            
            print(f"正在捕获第 {current_question} 题...")
            
            # 检查是否已经捕获过这个题号
            if current_question in captured_questions:
                print(f"题号 {current_question} 已经捕获过，可能已经到达最后一题")
                # 尝试继续点击下一题，看看是否有新题目
                pass
            else:
                # 捕获当前页面的HTML
                print("正在捕获页面HTML...")
                html_content = self.driver.page_source
                html_file_path = os.path.join(self.captured_html_dir, f"第{current_question}题.html")
                
                # 保存HTML到文件
                try:
                    with open(html_file_path, 'w', encoding='utf-8') as file:
                        file.write(html_content)
                    print(f"已保存第 {current_question} 题的HTML到: {html_file_path}")
                except Exception as e:
                    print(f"保存HTML文件时出错: {e}")
                
                # 记录已捕获的题号
                captured_questions.add(current_question)
                print(f"已捕获题号集合: {captured_questions}")
            
            # 检查是否已经到达最后一题
            if current_question >= total_questions:
                print(f"已到达最后一题（第{current_question}题，共{total_questions}题）")
                print(f"\n捕获完成，共捕获 {len(captured_questions)} 道题目")
                return True
            
            # 更新计数器
            question_count += 1
            
            # 尝试点击下一题按钮
            print("正在尝试点击下一题按钮...")
            next_button_clicked = False
            
            # 尝试多种可能的下一题按钮选择器
            next_button_selectors = [
                (By.ID, "next_btn"),
                (By.XPATH, "//a[contains(text(), '下一题')]"),
                (By.XPATH, "//button[contains(text(), '下一题')]"),
                (By.XPATH, "//a[contains(text(), '下一题')]/.."),
                (By.XPATH, "//button[contains(text(), '下一题')]/.."),
                (By.CSS_SELECTOR, "#next_btn")
            ]
            
            for i, selector in enumerate(next_button_selectors):
                try:
                    print(f"尝试第 {i+1} 种选择器: {selector}")
                    next_button = self.wait.until(
                        EC.element_to_be_clickable(selector)
                    )
                    if next_button and next_button.is_displayed():
                        # 使用JavaScript点击按钮，更可靠
                        print("找到下一题按钮，正在点击...")
                        self.driver.execute_script("arguments[0].click();", next_button)
                        print("已点击下一题按钮")
                        next_button_clicked = True
                        break
                except TimeoutException:
                    print(f"选择器 {i+1} 超时")
                    continue
                except Exception as e:
                    print(f"使用选择器 {i+1} 点击下一题按钮时出错: {e}")
                    continue
            
            # 如果无法点击下一题按钮，可能是已经到达最后一题
            if not next_button_clicked:
                print("无法点击下一题按钮，可能已经到达最后一题")
                print(f"\n捕获完成，共捕获 {len(captured_questions)} 道题目")
                return True
            
            # 等待页面加载
            print("等待页面加载...")
            if not self.wait_for_page_load():
                print("页面加载失败，继续尝试下一题")
                # 即使页面加载失败，也继续尝试下一题
        
        print(f"\n捕获完成，共捕获 {len(captured_questions)} 道题目")
        return True
    
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
    
    def convert_html_to_txt(self):
        """
        将所有HTML文件转换为单个TXT文件
        """
        # 获取所有HTML文件
        html_files = [f for f in os.listdir(self.captured_html_dir) if f.endswith('.html')]
        html_files.sort(key=lambda x: int(re.search(r'第(\d+)题\.html', x).group(1)))  # 按题号排序
        
        if not html_files:
            print(f"在目录 {self.captured_html_dir} 中没有找到HTML文件")
            return False
        
        print(f"找到 {len(html_files)} 个HTML文件")

        # 创建单个输出文件
        output_file = self.questions_txt_path
        
        # 转换每个HTML文件并追加到输出文件
        for i, html_file in enumerate(html_files):
            print(f"正在处理: {html_file}")
            
            # 构建文件路径
            html_path = os.path.join(self.captured_html_dir, html_file)
            
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
    
    def navigate_to_question(self, question_number):
        """导航到指定题号"""
        try:
            # 查找题号导航元素
            xpath = f"//div[@class='tihao']//li[contains(text(), '{question_number}')]"
            question_nav_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            question_nav_element.click()
            print(f"已导航到第 {question_number} 题")
            
            # 等待页面加载完成，通过检查题目标题元素
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h2.h4.fch2"))
                )
            except:
                # 如果题目标题元素加载失败，尝试等待其他元素
                try:
                    self.wait.until(
                        EC.presence_of_element_located((By.XPATH, f"//div[@class='tihao']//li[contains(text(), '{question_number}') and contains(@class, 'active')]"))
                    )
                except:
                    pass
            
            return True
        except Exception as e:
            print(f"导航到第 {question_number} 题时出错: {e}")
            return False
    
    def select_answer(self, answer):
        """选择答案"""
        try:
            # 根据答案选择对应的选项
            xpath = f"//label[contains(@class, 'el-radio') and .//input[@value='{answer}']]"
            option_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            option_element.click()
            # 添加0.05秒等待，确保选择操作完成
            time.sleep(0.05)
            print(f"已选择选项: {answer}")
            return True
        except Exception as e:
            print(f"选择答案 {answer} 时出错: {e}")
            return False
    
    def parse_answers_file(self):
        """解析答案文件"""
        answers = {}
        try:
            with open(self.answers_txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('.')
                        if len(parts) >= 2:
                            question_num = int(parts[0])
                            answer = parts[1].strip().upper()
                            answers[question_num] = answer
            return answers
        except Exception as e:
            print(f"解析答案文件时出错: {e}")
            return {}
    
    def answer_all_questions(self):
        """回答所有题目"""
        try:
            # 确保浏览器已打开
            if not self.driver:
                print("浏览器未打开，正在重新打开...")
                if not self.open_exam_page():
                    return False
            
            # 解析答案文件
            answers = self.parse_answers_file()
            if not answers:
                print("未能解析到答案，请检查答案文件")
                return False
            
            print(f"共解析到 {len(answers)} 个答案")
            
            # 获取所有需要回答的题号并排序
            question_numbers = sorted(answers.keys())
            
            # 循环处理每道题目
            for i, question_num in enumerate(question_numbers):
                print(f"正在处理第 {question_num} 题 ({i+1}/{len(question_numbers)})")
                
                # 导航到指定题号
                if not self.navigate_to_question(question_num):
                    print(f"无法导航到第 {question_num} 题，跳过")
                    continue
                
                # 获取答案
                answer = answers.get(question_num)
                if not answer:
                    print(f"第 {question_num} 题没有找到答案，跳过")
                    continue
                
                # 选择答案
                if not self.select_answer(answer):
                    print(f"第 {question_num} 题选择答案失败，跳过")
                    continue
                
                # 记录已答题号
                self.answered_questions.add(question_num)
                
                # 如果不是最后一题，导航到下一题
                if i < len(question_numbers) - 1:
                    next_question = question_numbers[i + 1]
                    if not self.navigate_to_question(next_question):
                        print(f"无法导航到第 {next_question} 题")
                        break
                    self.current_question = next_question
            
            print(f"答题完成，共回答 {len(self.answered_questions)} 道题")
            return True
            
        except Exception as e:
            print(f"答题过程中出错: {e}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("浏览器已关闭")
        
        # 清理临时用户数据目录
        if hasattr(self, 'temp_user_data_dir') and os.path.exists(self.temp_user_data_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_user_data_dir)
                print(f"已清理临时用户数据目录: {self.temp_user_data_dir}")
            except Exception as e:
                print(f"清理临时用户数据目录失败: {e}")
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*50)
        print("考试工具套件 - 主菜单")
        print("="*50)
        print("1. 批量捕获所有题目的HTML")
        print("2. 批量格式化题目HTML为TXT")
        print("3. 批量选择答案")
        print("4. 关闭浏览器并退出")
        print("="*50)
    
    def run(self):
        """运行主程序"""
        print("欢迎使用考试工具套件！")
        print("浏览器已打开到考试登录页面，请登录后选择功能。")
        
        while True:
            self.show_menu()
            choice = input("请选择功能 (1-4): ").strip()
            
            if choice == "1":
                print("\n开始批量捕获所有题目的HTML...")
                self.capture_all_questions()
                
            elif choice == "2":
                print("\n开始批量格式化题目HTML为TXT...")
                self.convert_html_to_txt()
                
            elif choice == "3":
                print("\n开始批量选择答案...")
                self.answer_all_questions()
                
            elif choice == "4":
                print("\n正在关闭浏览器...")
                self.close_browser()
                print("感谢使用考试工具套件，再见！")
                break
                
            else:
                print("\n无效的选择，请重新输入！")

def main():
    # 创建考试工具套件实例
    tool = ExamToolSuite()
    
    try:
        # 运行主程序
        tool.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保浏览器关闭
        tool.close_browser()

if __name__ == "__main__":
    main()