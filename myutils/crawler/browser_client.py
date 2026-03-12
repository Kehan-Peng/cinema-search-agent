"""基于 Selenium + WebDriver Manager 的浏览器客户端，用于绕过豆瓣反爬虫"""
from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    raise RuntimeError("缺少 selenium 或 webdriver-manager 依赖，请执行: pip install selenium webdriver-manager")


class DoubanBrowserClient:
    """使用 Selenium + WebDriver Manager 绕过豆瓣反爬虫的浏览器客户端"""

    def __init__(self, headless: bool = True, min_delay: float = 5.0, max_delay: float = 10.0):
        self.headless = headless
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.driver: Optional[webdriver.Chrome] = None
        self.request_count = 0

    def _init_driver(self) -> None:
        """初始化浏览器驱动"""
        if self.driver is not None:
            return

        options = Options()
        if self.headless:
            options.add_argument("--headless=new")

        # 添加反检测参数
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")

        # 设置用户代理
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        try:
            # 使用 WebDriver Manager 自动管理 ChromeDriver 版本
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            # 执行 CDP 命令隐藏 webdriver 特征
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })

            # 设置页面加载超时
            self.driver.set_page_load_timeout(30)
            print("浏览器驱动初始化成功")
        except Exception as e:
            raise RuntimeError(f"浏览器驱动初始化失败: {e}")

    def _adaptive_delay(self) -> None:
        """自适应延迟策略"""
        self.request_count += 1
        base_delay = random.uniform(self.min_delay, self.max_delay)

        # 每3个请求增加额外延迟
        if self.request_count % 3 == 0:
            base_delay += random.uniform(3.0, 6.0)

        # 每5个请求增加更长延迟
        if self.request_count % 5 == 0:
            base_delay += random.uniform(8.0, 12.0)

        print(f"等待 {base_delay:.1f} 秒...")
        time.sleep(base_delay)

    def get_html(self, url: str, wait_selector: Optional[str] = None, wait_timeout: int = 10) -> str:
        """
        获取页面HTML内容

        Args:
            url: 目标URL
            wait_selector: 等待的CSS选择器（可选）
            wait_timeout: 等待超时时间（秒）

        Returns:
            页面HTML内容
        """
        self._init_driver()

        try:
            print(f"正在访问: {url}")
            self.driver.get(url)

            # 如果指定了选择器，等待元素加载
            if wait_selector:
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )

            # 检查是否被重定向到验证页面
            current_url = self.driver.current_url
            if "sec.douban.com" in current_url:
                raise RuntimeError(f"触发豆瓣反爬虫验证，被重定向到: {current_url}")

            # 检查页面内容是否包含验证码
            page_source = self.driver.page_source
            if "安全验证" in page_source or "请输入验证码" in page_source:
                raise RuntimeError("页面包含验证码，需要人工处理")

            self._adaptive_delay()
            return page_source

        except Exception as e:
            print(f"获取页面失败: {e}")
            raise

    def close(self) -> None:
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                print("浏览器已关闭")
            except Exception as e:
                print(f"关闭浏览器时出错: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
