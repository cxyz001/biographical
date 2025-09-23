import base64
import os
from PIL import Image
import io

# 创建images文件夹（如果不存在）
os.makedirs('images', exist_ok=True)

# 将图片文件保存到images文件夹中
def save_image_from_clipboard():
    try:
        # 从剪贴板获取图片
        from PIL import ImageGrab
        img = ImageGrab.grabclipboard()
        
        if img:
            # 保存图片
            img.save('images/avatar.jpg', 'JPEG')
            print("头像已保存到 images/avatar.jpg")
            return True
        else:
            print("剪贴板中没有图片，请复制图片到剪贴板后重试")
            return False
    except Exception as e:
        print(f"保存图片时出错: {e}")
        return False

if __name__ == "__main__":
    save_image_from_clipboard() 