"""
iWrite评分器 - 使用浏览器自动化提交作文
"""
import json
import time
from typing import Dict, List
from pathlib import Path
from core.base import Scorer, Essay


class IwriteScorer(Scorer):
    """
    iWrite评分器 (浏览器自动化方式)
    
    由于iWrite没有公开API，需要使用浏览器自动化提交作文
    需要配置浏览器路径和账号
    
    注意: 此评分器需要用户手动登录一次，之后可以使用cookie
    """
    
    def __init__(self, browser_type: str = "chrome"):
        super().__init__("iWrite(Auto)")
        self.browser_type = browser_type
        self.cookies_file = Path(__file__).parent.parent / "data" / "iwrite_cookies.json"
        self.logged_in = False
    
    def login_with_cookies(self, cookies: List[Dict] = None):
        """
        使用保存的cookies登录
        
        需要先用浏览器手动登录iWrite，然后导出cookies
        """
        if cookies is None and self.cookies_file.exists():
            with open(self.cookies_file, "r") as f:
                cookies = json.load(f)
        
        self.cookies = cookies
        self.logged_in = True
    
    def score(self, essay: Essay) -> Dict:
        """
        使用浏览器自动化提交作文并获取评分
        
        由于需要真实浏览器环境，这里提供框架代码
        实际使用时需要安装playwright: pip install playwright
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("  [!] 需要安装playwright: pip install playwright && playwright install")
            return self._manual_submission_prompt(essay)
        
        result = self._submit_via_browser(essay)
        return result
    
    def _submit_via_browser(self, essay: Essay) -> Dict:
        """
        通过浏览器自动化提交作文
        
        步骤:
        1. 打开iWrite登录页
        2. 如果有cookies则自动登录，否则提示手动登录
        3. 找到"快速体验"入口
        4. 粘贴作文内容并提交
        5. 提取评分结果
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            # 加载cookies
            if hasattr(self, 'cookies') and self.cookies:
                context.add_cookies(self.cookies)
            
            page = context.new_page()
            
            try:
                # 打开iWrite快速体验页
                page.goto("https://iwrite.unipus.cn/login/correctingExperience", timeout=30000)
                time.sleep(3)
                
                # 粘贴作文
                # 需要找到textarea元素
                page.click("textarea", timeout=5000)
                page.fill("textarea", essay.content)
                time.sleep(1)
                
                # 点击批改按钮
                page.click("button:has-text('批改')", timeout=10000)
                time.sleep(5)
                
                # 等待评分结果出现
                page.wait_for_selector(".score", timeout=15000)
                
                # 提取分数
                score_text = page.text_content(".score")
                feedback = page.text_content(".feedback")
                
                return {
                    "score": float(score_text) if score_text else 0,
                    "dimensions": {"language": 0, "content": 0, "structure": 0, "technical": 0},
                    "feedback": feedback,
                    "errors": [],
                }
                
            except Exception as e:
                print(f"  [!] Browser automation error: {e}")
                return self._manual_submission_prompt(essay)
            
            finally:
                browser.close()
    
    def _manual_submission_prompt(self, essay: Essay) -> Dict:
        """
        当自动化失败时，提示用户手动提交
        """
        print("\n" + "="*60)
        print("iWrite评分需要手动提交")
        print("="*60)
        print(f"作文标题: {essay.title}")
        print(f"作文内容:\n{essay.content[:200]}...")
        print(f"\n请访问: https://iwrite.unipus.cn/login/correctingExperience")
        print("登录后点击'快速体验'，粘贴作文内容，点击'批改'")
        print("="*60 + "\n")
        
        return {
            "score": 0,
            "dimensions": {"language": 0, "content": 0, "structure": 0, "technical": 0},
            "feedback": "Manual submission required",
            "errors": [],
        }
