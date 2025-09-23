import os
import subprocess

def generate_optimal_pdf(html_path, pdf_path):
    try:
        # 尝试使用Chrome生成PDF
        chrome_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        ]
        
        chrome_exe = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_exe = path
                break
        
        if chrome_exe is None:
            print("未找到Chrome浏览器，无法转换为PDF")
            return False
        
        # 构建最优化的PDF生成命令
        cmd = [
            chrome_exe,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',     # 禁用页眉页脚
            '--print-to-pdf-no-header',   # 禁用页眉
            '--no-margins',               # 禁用边距
            '--disable-print-preview',    # 禁用打印预览
            '--run-all-compositor-stages-before-draw',
            '--print-to-pdf-no-footer',   # 禁用页脚
            '--no-headers',               # 禁用HTTP请求头
            '--disable-web-security',     # 禁用Web安全策略
            '--disable-extensions',       # 禁用扩展
            '--disable-breakpad',         # 禁用崩溃报告
            f'--print-to-pdf={os.path.abspath(pdf_path)}',
            f'file:///{os.path.abspath(html_path)}'
        ]
        
        # 执行命令
        subprocess.run(cmd, check=True)
        print(f"已生成优化的PDF文档: {pdf_path}")
        return True
    
    except Exception as e:
        print(f"生成PDF失败: {e}")
        return False

if __name__ == "__main__":
    html_path = 'resume.html'
    pdf_path = 'resume_final.pdf'
    
    print("正在生成最终优化版PDF...")
    generate_optimal_pdf(html_path, pdf_path)
    print("完成！请查看生成的PDF文件。") 