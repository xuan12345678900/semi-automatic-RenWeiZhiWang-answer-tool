import os
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ExamCaptureTool:
    def __init__(self, chromedriver_path=None):
        """
        初始化考试捕获工具
        
        参数:
            chromedriver_path: chromedriver.exe的路径，如果为None则假设在系统PATH中
        """
        # 设置Chrome选项
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")  # 最大化窗口
        
        # 创建临时用户数据目录，避免Chrome用户数据目录冲突
        temp_dir = tempfile.mkdtemp()
        self.chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        self.chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        self.chrome_options.add_argument("--disable-background-timer-throttling")
        self.chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        self.chrome_options.add_argument("--disable-renderer-backgrounding")
        self.chrome_options.add_argument("--disable-field-trial-config")
        self.chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # 初始化WebDriver
        if chromedriver_path:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        else:
            self.driver = webdriver.Chrome(options=self.chrome_options)
        
        # 设置等待时间
        self.wait = WebDriverWait(self.driver, 10)
        
        # 存储捕获的HTML文件路径
        self.captured_html_dir = r"c:\Users\ASUS\Desktop\做题\captured_html"
        
        # 确保目录存在
        if not os.path.exists(self.captured_html_dir):
            os.makedirs(self.captured_html_dir)
    
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
        # 这里需要根据实际的考试页面URL进行修改
        exam_url = "https://exam.ipmph.com/"
        print(f"正在打开考试页面: {exam_url}")
        self.driver.get(exam_url)
        
        # 等待页面加载
        if not self.wait_for_page_load():
            print("页面加载失败")
            return False
        
        print("页面加载成功")
        print("请手动登录并导航到考试页面，准备好后请按Enter键开始捕获HTML...")
        input()
        print("开始捕获HTML...")
        
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
        
        return 0
    
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
        
        return 0
    
    def capture_all_questions(self):
        """
        捕获所有题目的HTML
        """
        # 首先打开考试页面
        if not self.open_exam_page():
            print("无法打开考试页面")
            return False
        
        # 获取总题数
        print("正在获取总题数...")
        total_questions = self.get_total_questions()
        if total_questions > 0:
            print(f"检测到总题数: {total_questions}")
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
                print("正在关闭浏览器...")
                self.close()
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
                print("正在关闭浏览器...")
                self.close()
                return True
            
            # 等待页面加载
            print("等待页面加载...")
            if not self.wait_for_page_load():
                print("页面加载失败，继续尝试下一题")
                # 即使页面加载失败，也继续尝试下一题
        
        print(f"\n捕获完成，共捕获 {len(captured_questions)} 道题目")
        return True
    
    def close(self):
        """
        关闭浏览器
        """
        self.driver.quit()

def main():
    # 创建考试捕获工具实例
    # 如果chromedriver.exe不在系统PATH中，请提供完整路径
    chromedriver_path = r"c:\Users\ASUS\Desktop\做题\chromedriver-win64\chromedriver.exe"
    print(f"正在初始化考试捕获工具，使用ChromeDriver路径: {chromedriver_path}")
    
    # 删除captured_html目录下的所有文件
    captured_html_dir = r"c:\Users\ASUS\Desktop\做题\captured_html"
    if os.path.exists(captured_html_dir):
        print(f"正在删除 {captured_html_dir} 目录下的所有文件...")
        for filename in os.listdir(captured_html_dir):
            file_path = os.path.join(captured_html_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"已删除文件: {file_path}")
            except Exception as e:
                print(f"删除文件 {file_path} 时出错: {e}")
        print("已清理captured_html目录")
    else:
        print(f"目录 {captured_html_dir} 不存在，将创建新目录")
    
    try:
        exam_capture = ExamCaptureTool(chromedriver_path)
        print("考试捕获工具初始化成功")
        
        # 捕获所有题目
        print("开始捕获所有题目...")
        exam_capture.capture_all_questions()
        print("题目捕获完成")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭浏览器
        try:
            print("正在关闭浏览器...")
            exam_capture.close()
            print("浏览器已关闭")
        except:
            pass

if __name__ == "__main__":
    main()