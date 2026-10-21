# -*- coding: utf-8 -*-
import os
import subprocess
import datetime

def generate_pdf(html_path, pdf_path):
    """使用Chrome将HTML转换为PDF"""
    try:
        # Chrome可能的安装路径
        chrome_paths = [
            'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
            'C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'.format(os.getenv('USERNAME')),
        ]
        
        chrome_exe = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_exe = path
                break
        
        if chrome_exe is None:
            print("未找到Chrome浏览器，无法转换为PDF")
            print("请安装Google Chrome浏览器")
            return False
        
        # 构建PDF生成命令
        cmd = [
            chrome_exe,
            '--headless',
            '--disable-gpu',
            '--no-pdf-header-footer',
            '--print-to-pdf-no-header',
            '--no-margins',
            '--disable-print-preview',
            '--run-all-compositor-stages-before-draw',
            '--print-to-pdf-no-footer',
            '--no-headers',
            '--disable-web-security',
            '--disable-extensions',
            '--disable-breakpad',
            '--print-to-pdf={}'.format(os.path.abspath(pdf_path)),
            'file:///{}'.format(os.path.abspath(html_path).replace('\\', '/'))
        ]
        
        print("正在生成PDF...")
        subprocess.call(cmd)
        
        if os.path.exists(pdf_path):
            print("PDF生成成功: {}".format(pdf_path))
            return True
        else:
            print("PDF生成失败")
            return False
    
    except Exception as e:
        print("生成PDF时出错: {}".format(e))
        return False

if __name__ == "__main__":
    # 获取当前日期
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # HTML和PDF文件名（保持一致）
    html_filename = '李务梅简历_{}.html'.format(current_date)
    pdf_filename = '李务梅简历_{}.pdf'.format(current_date)
    
    print("="*60)
    print("李务梅简历PDF生成工具")
    print("="*60)
    print("HTML文件: {}".format(html_filename))
    print("输出PDF: {}".format(pdf_filename))
    print("="*60)
    
    if not os.path.exists(html_filename):
        print("错误：找不到HTML文件 {}".format(html_filename))
        print("请确保HTML文件存在")
    else:
        result = generate_pdf(html_filename, pdf_filename)
        if result:
            print("="*60)
            print("完成！请查看生成的PDF文件")
            print("文件位置: {}".format(os.path.abspath(pdf_filename)))
            print("="*60)
        else:
            print("="*60)
            print("生成失败，请检查错误信息")
            print("="*60)



