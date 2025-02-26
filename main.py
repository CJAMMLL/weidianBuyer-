import sys
import re
import time
from datetime import datetime
import ntplib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIntValidator, QKeyEvent, QIcon
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import zipfile
import io

def download_chromedriver():
    """下载并解压ChromeDriver"""
    url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/133.0.6943.127/win64/chromedriver-win64.zip"
    try:
        # 下载ChromeDriver
        response = requests.get(url)
        if response.status_code == 200:
            # 解压zip文件
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # 提取chromedriver.exe
                for file in zip_ref.namelist():
                    if file.endswith('chromedriver.exe'):
                        with zip_ref.open(file) as source, open('chromedriver.exe', 'wb') as target:
                            target.write(source.read())
            return True
    except Exception as e:
        print(f"下载ChromeDriver失败: {str(e)}")
    return False

class TimeInputField(QLineEdit):
    def __init__(self, next_field=None, prev_field=None):
        super().__init__()
        self.next_field = next_field
        self.prev_field = prev_field
        
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right and self.next_field:
            self.next_field.setFocus()
        elif event.key() == Qt.Key_Left and self.prev_field:
            self.prev_field.setFocus()
        else:
            super().keyPressEvent(event)

class WeidianShopper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.driver = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_current_time)
        self.timer.start(100)  # 每100ms更新一次时间
        self.ntp_client = ntplib.NTPClient()
        self.time_offset = 0
        self.sync_time()
        
        # 设置程序图标
        try:
            # 使用绝对路径加载图标
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'icons', 'app.ico'))
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.log_message(f"加载程序图标失败: {str(e)}")
        
    def initUI(self):
        self.setWindowTitle('weidianBuyer微店买手v1.0')
        self.setGeometry(300, 300, 800, 400)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 时间显示组
        time_group = QHBoxLayout()
        self.current_time_label = QLabel('当前时间: ')
        self.target_time_label = QLabel('目标时间: ')
        time_group.addWidget(self.current_time_label)
        time_group.addWidget(self.target_time_label)
        layout.addLayout(time_group)
        
        # URL输入组
        url_group = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('将微店商品链接粘贴到这里')
        url_group.addWidget(self.url_input)
        layout.addLayout(url_group)
        
        # 时间输入组
        time_input_group = QHBoxLayout()
        
        # 创建所有输入框
        self.year_input = TimeInputField()
        self.month_input = TimeInputField()
        self.day_input = TimeInputField()
        self.hour_input = TimeInputField()
        self.minute_input = TimeInputField()
        self.second_input = TimeInputField()
        self.microsecond_input = TimeInputField()
        
        # 设置默认值
        self.year_input.setText('2025')
        self.second_input.setText('00')
        self.microsecond_input.setText('000000')
        
        # 设置输入框的前后关系
        self.year_input.next_field = self.month_input
        self.month_input.prev_field = self.year_input
        self.month_input.next_field = self.day_input
        self.day_input.prev_field = self.month_input
        self.day_input.next_field = self.hour_input
        self.hour_input.prev_field = self.day_input
        self.hour_input.next_field = self.minute_input
        self.minute_input.prev_field = self.hour_input
        self.minute_input.next_field = self.second_input
        self.second_input.prev_field = self.minute_input
        self.second_input.next_field = self.microsecond_input
        self.microsecond_input.prev_field = self.second_input
        
        # 年份输入框
        year_layout = QVBoxLayout()
        year_label = QLabel('年(YYYY)')
        self.year_input.setMaxLength(4)
        self.year_input.setValidator(QIntValidator(2000, 9999))
        self.year_input.setFixedWidth(60)
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_input)
        time_input_group.addLayout(year_layout)
        
        time_input_group.addWidget(QLabel('-'))
        
        # 月份输入框
        month_layout = QVBoxLayout()
        month_label = QLabel('月(MM)')
        self.month_input.setMaxLength(2)
        self.month_input.setValidator(QIntValidator(1, 12))
        self.month_input.setFixedWidth(40)
        month_layout.addWidget(month_label)
        month_layout.addWidget(self.month_input)
        time_input_group.addLayout(month_layout)
        
        time_input_group.addWidget(QLabel('-'))
        
        # 日期输入框
        day_layout = QVBoxLayout()
        day_label = QLabel('日(DD)')
        self.day_input.setMaxLength(2)
        self.day_input.setValidator(QIntValidator(1, 31))
        self.day_input.setFixedWidth(40)
        day_layout.addWidget(day_label)
        day_layout.addWidget(self.day_input)
        time_input_group.addLayout(day_layout)
        
        time_input_group.addWidget(QLabel(' '))
        
        # 小时输入框
        hour_layout = QVBoxLayout()
        hour_label = QLabel('时(HH)')
        self.hour_input.setMaxLength(2)
        self.hour_input.setValidator(QIntValidator(0, 23))
        self.hour_input.setFixedWidth(40)
        hour_layout.addWidget(hour_label)
        hour_layout.addWidget(self.hour_input)
        time_input_group.addLayout(hour_layout)
        
        time_input_group.addWidget(QLabel(':'))
        
        # 分钟输入框
        minute_layout = QVBoxLayout()
        minute_label = QLabel('分(mm)')
        self.minute_input.setMaxLength(2)
        self.minute_input.setValidator(QIntValidator(0, 59))
        self.minute_input.setFixedWidth(40)
        minute_layout.addWidget(minute_label)
        minute_layout.addWidget(self.minute_input)
        time_input_group.addLayout(minute_layout)
        
        time_input_group.addWidget(QLabel(':'))
        
        # 秒输入框
        second_layout = QVBoxLayout()
        second_label = QLabel('秒(ss)')
        self.second_input.setMaxLength(2)
        self.second_input.setValidator(QIntValidator(0, 59))
        self.second_input.setFixedWidth(40)
        second_layout.addWidget(second_label)
        second_layout.addWidget(self.second_input)
        time_input_group.addLayout(second_layout)
        
        time_input_group.addWidget(QLabel('.'))
        
        # 微秒输入框
        microsecond_layout = QVBoxLayout()
        microsecond_label = QLabel('微秒(ssssss)')
        self.microsecond_input.setMaxLength(6)
        self.microsecond_input.setValidator(QIntValidator(0, 999999))
        self.microsecond_input.setFixedWidth(70)
        self.microsecond_input.setText('000000')  # 设置默认值
        microsecond_layout.addWidget(microsecond_label)
        microsecond_layout.addWidget(self.microsecond_input)
        time_input_group.addLayout(microsecond_layout)
        
        time_input_group.addStretch()
        layout.addLayout(time_input_group)
        
        # 控制组
        control_group = QHBoxLayout()
        self.reserve_btn = QPushButton('预约')
        self.reset_btn = QPushButton('重置')
        
        self.reserve_btn.clicked.connect(self.start_reservation)
        self.reset_btn.clicked.connect(self.reset_reservation)
        
        control_group.addWidget(self.reserve_btn)
        control_group.addWidget(self.reset_btn)
        layout.addLayout(control_group)
        
        # 日志显示区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # 设置样式
        self.reserve_btn.setStyleSheet('background-color: #4CAF50; color: white;')
        self.reset_btn.setStyleSheet('background-color: #9E9E9E; color: white;')
        
    def sync_time(self):
        try:
            response = self.ntp_client.request('ntp.aliyun.com')
            self.time_offset = response.offset
            self.log_message(f"时间同步成功，偏移量: {self.time_offset:.3f}秒")
        except:
            self.log_message("时间同步失败，使用本地时间")
            
    def get_current_time(self):
        return datetime.now().timestamp() + self.time_offset
        
    def update_current_time(self):
        current_time = datetime.fromtimestamp(self.get_current_time())
        self.current_time_label.setText(f'当前时间: {current_time.strftime("%Y-%m-%d %H:%M:%S.%f")}')
        
    def get_target_time_str(self):
        # 获取并验证所有输入框的值
        year = self.year_input.text().zfill(4)
        month = self.month_input.text().zfill(2)
        day = self.day_input.text().zfill(2)
        hour = self.hour_input.text().zfill(2)
        minute = self.minute_input.text().zfill(2)
        second = self.second_input.text().zfill(2)
        microsecond = self.microsecond_input.text().zfill(6)
        
        # 拼接完整的时间字符串
        return f"{year}-{month}-{day} {hour}:{minute}:{second}.{microsecond}"
        
    def validate_time_inputs(self):
        # 检查所有输入框是否都已填写
        if not all([
            self.year_input.text(),
            self.month_input.text(),
            self.day_input.text(),
            self.hour_input.text(),
            self.minute_input.text(),
            self.second_input.text(),
            self.microsecond_input.text()
        ]):
            return False
            
        try:
            # 获取完整的时间字符串
            time_str = self.get_target_time_str()
            # 尝试解析时间字符串
            datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
            return True
        except ValueError:
            return False
            
    def init_browser(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.log_message("正在初始化浏览器...")
            
            try:
                # 检查ChromeDriver是否存在
                if not os.path.exists("chromedriver.exe"):
                    self.log_message("未找到chromedriver.exe，正在自动下载...")
                    if download_chromedriver():
                        self.log_message("ChromeDriver下载成功")
                    else:
                        self.log_message("ChromeDriver自动下载失败")
                        self.log_message("请手动下载ChromeDriver：")
                        self.log_message("https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/133.0.6943.127/win64/chromedriver-win64.zip")
                        raise Exception("ChromeDriver不存在")
                    
                service = Service("chromedriver.exe")
                self.log_message("使用本地ChromeDriver")
                
                self.driver = webdriver.Chrome(service=service, options=options)
                self.log_message("浏览器初始化成功")
            except Exception as e:
                if "version" in str(e).lower():
                    self.log_message("ChromeDriver版本与Chrome浏览器版本不匹配")
                    self.log_message("请确保下载的是133.0.6943.127版本的ChromeDriver")
                self.log_message(f"浏览器初始化失败: {str(e)}")
                raise
                
        except Exception as e:
            self.log_message(f"浏览器初始化过程出错: {str(e)}")
            raise
        
    def start_reservation(self):
        try:
            # 检查URL输入
            product_url = self.url_input.text().strip()
            if not product_url:
                self.log_message("请先粘贴商品链接")
                return
                
            # 检查时间输入
            if not self.validate_time_inputs():
                self.log_message("请填写完整的时间信息，并确保格式正确")
                return
                
            target_time_str = self.get_target_time_str()
            target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S.%f")
            self.target_time_label.setText(f'目标时间: {target_time_str}')
            self.log_message(f"预约成功，抢购时间：{target_time_str}")
            
            try:
                # 初始化浏览器
                self.init_browser()
                # 打开商品页面
                self.driver.get(product_url)
                self.log_message("已打开商品页面，请手动完成：")
                self.log_message("1. 登录账号")
                self.log_message("2. 添加商品到购物车")
                self.log_message("3. 点击购物车按钮进入购物车页面")
                self.log_message("4. 手动勾选要购买的商品")
            except Exception as e:
                self.log_message(f"浏览器初始化失败: {str(e)}")
                return
            
            # 开始监控时间
            self.monitor_timer = QTimer()
            self.monitor_timer.timeout.connect(lambda: self.check_time(target_time))
            self.monitor_timer.start(100)  # 每100ms检查一次
            
        except Exception as e:
            self.log_message(f"预约过程出错: {str(e)}")
            if self.driver:
                self.driver.quit()
                self.driver = None
                
    def check_time(self, target_time):
        current_time = datetime.fromtimestamp(self.get_current_time())
        if current_time >= target_time:
            self.monitor_timer.stop()
            self.execute_purchase()
            
    def execute_purchase(self):
        try:
            # 尝试定位结算按钮
            try_count = 0
            max_tries = 3
            checkout_btn = None
            
            while try_count < max_tries and not checkout_btn:
                try:
                    # 使用多种XPath表达式尝试定位结算按钮
                    xpaths = [
                        "//button[contains(text(), '结算')]",  # 按钮中包含"结算"文本
                        "//div[contains(text(), '结算')]",     # div中包含"结算"文本
                        "//span[contains(text(), '结算')]",    # span中包含"结算"文本
                        "//*[contains(text(), '结算')]"        # 任何包含"结算"文本的元素
                    ]
                    
                    for xpath in xpaths:
                        try:
                            checkout_btn = WebDriverWait(self.driver, 1).until(
                                EC.element_to_be_clickable((By.XPATH, xpath))
                            )
                            if checkout_btn:
                                break
                        except:
                            continue
                            
                    if checkout_btn:
                        # 使用JavaScript点击按钮
                        self.driver.execute_script("arguments[0].click();", checkout_btn)
                        self.log_message("已点击结算按钮")
                        break
                    else:
                        raise Exception("未找到结算按钮")
                        
                except Exception as e:
                    try_count += 1
                    if try_count < max_tries:
                        self.log_message(f"第{try_count}次尝试定位结算按钮失败，正在重试...")
                        time.sleep(0.5)
                    else:
                        self.log_message("未能找到结算按钮")
                        return
                        
            # 等待并点击提交订单按钮
            try_count = 0
            submit_btn = None
            
            while try_count < max_tries and not submit_btn:
                try:
                    # 使用多种XPath表达式尝试定位提交订单按钮
                    xpaths = [
                        "//button[contains(text(), '提交订单')]",  # 按钮中包含"提交订单"文本
                        "//div[contains(text(), '提交订单')]",     # div中包含"提交订单"文本
                        "//span[contains(text(), '提交订单')]",    # span中包含"提交订单"文本
                        "//*[contains(text(), '提交订单')]"        # 任何包含"提交订单"文本的元素
                    ]
                    
                    for xpath in xpaths:
                        try:
                            submit_btn = WebDriverWait(self.driver, 1).until(
                                EC.element_to_be_clickable((By.XPATH, xpath))
                            )
                            if submit_btn:
                                break
                        except:
                            continue
                            
                    if submit_btn:
                        # 使用JavaScript点击按钮
                        self.driver.execute_script("arguments[0].click();", submit_btn)
                        self.log_message("已点击提交订单按钮")
                        break
                    else:
                        raise Exception("未找到提交订单按钮")
                        
                except Exception as e:
                    try_count += 1
                    if try_count < max_tries:
                        self.log_message(f"第{try_count}次尝试定位提交订单按钮失败，正在重试...")
                        time.sleep(0.5)
                    else:
                        self.log_message("未能找到提交订单按钮")
                        return
                        
            self.log_message("抢购完成！")
            
        except Exception as e:
            self.log_message(f"抢购过程出错: {str(e)}")
            # 打印详细的错误信息
            import traceback
            self.log_message(f"详细错误信息: {traceback.format_exc()}")
            
    def reset_reservation(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            
        # 清空URL输入框
        self.url_input.clear()
        
        # 只清空部分时间输入框，保留默认值的不清空
        self.month_input.clear()
        self.day_input.clear()
        self.hour_input.clear()
        self.minute_input.clear()
        
        self.target_time_label.setText('目标时间: ')
        self.log_message("已重置，请重新预约")
        
    def log_message(self, message):
        current_time = datetime.now().strftime("%H:%M:%S.%f")
        self.log_area.append(f"[{current_time}] {message}")
        
    def closeEvent(self, event):
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WeidianShopper()
    window.show()
    sys.exit(app.exec_()) 