#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re
import os
import sys
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

class ExamAnswerToolFixed:
    def __init__(self, driver_path=None, exam_url=None, answers_file=None):
        # 使用指定的chromedriver路径
        self.driver_path = driver_path or r"c:\Users\ASUS\Desktop\做题\chromedriver-win64\chromedriver.exe"
        self.exam_url = exam_url or "https://exam.ipmph.com/front/myschool/index.html#/login?Referer=https%3A%2F%2Fexam.ipmph.com%2Fexamzcms%2F"
        self.answers_file = answers_file or os.path.join(os.path.dirname(os.path.abspath(__file__)), "answers.txt")
        self.driver = None
        self.wait = None
        self.answered_questions = set()
        self.current_question = 1
        self.total_questions = 100
        self.initialize_browser()
    
    def initialize_browser(self):
        """初始化浏览器"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--start-maximized")
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
        
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 10)
        
    def get_current_question_number(self):
        """获取当前题号"""
        try:
            # 尝试从页面标题获取题号
            title = self.driver.title
            match = re.search(r'第(\d+)题', title)
            if match:
                return int(match.group(1))
            
            # 尝试从URL获取题号
            url = self.driver.current_url
            match = re.search(r'question_id=(\d+)', url)
            if match:
                return int(match.group(1))
                
            # 尝试从页面内容获取题号
            try:
                question_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h2.h4.fch2"))
                )
                question_text = question_element.text
                match = re.search(r'(\d+)\.', question_text)
                if match:
                    return int(match.group(1))
            except:
                pass
                
            # 如果以上方法都失败，返回当前记录的题号
            return self.current_question
        except:
            return self.current_question
    
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
    
    def select_answer_and_next(self, answer, next_question=None):
        """选择答案并导航到下一题"""
        # 选择答案
        if not self.select_answer(answer):
            return False
            
        # 记录已答题号
        current_question = self.get_current_question_number()
        self.answered_questions.add(current_question)
        
        # 如果指定了下一题，则导航到该题
        if next_question:
            if not self.navigate_to_question(next_question):
                print(f"无法导航到第 {next_question} 题")
                return False
            self.current_question = next_question
        else:
            # 如果没有指定下一题，则自动导航到下一题
            next_question = current_question + 1
            if next_question <= self.total_questions:
                if not self.navigate_to_question(next_question):
                    print(f"无法导航到第 {next_question} 题")
                    return False
                self.current_question = next_question
        
        return True
    
    def parse_answers_file(self):
        """解析答案文件"""
        answers = {}
        try:
            with open(self.answers_file, 'r', encoding='utf-8') as f:
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
            # 打开考试页面
            self.driver.get(self.exam_url)
            
            # 等待页面加载完成，通过检查登录按钮或页面标题
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '登录')]"))
                )
            except:
                try:
                    self.wait.until(
                        EC.title_contains("登录")
                    )
                except:
                    pass
            
            # 等待用户按下回车键开始答题
            print("页面已加载，请检查页面是否正常。按Enter键开始答题...")
            input()
            
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
    
    def keep_browser_open(self):
        """保持浏览器打开"""
        print("答题完成，浏览器将保持打开状态。按Enter键关闭浏览器...")
        input()
        self.close_browser()

def main():
    # 创建答题工具实例
    tool = ExamAnswerToolFixed()
    
    try:
        # 回答所有题目
        success = tool.answer_all_questions()
        
        if success:
            print("答题成功完成！")
        else:
            print("答题过程中遇到问题，请检查错误信息。")
            
        # 保持浏览器打开
        tool.keep_browser_open()
        
    except Exception as e:
        print(f"程序运行出错: {e}")
        tool.keep_browser_open()

if __name__ == "__main__":
    main()