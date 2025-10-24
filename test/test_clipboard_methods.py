#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试剪贴板复制功能，解决中文乱码问题
"""

import subprocess
import tempfile
import os

def test_clipboard_method_1(text):
    """方法1：使用Windows clip命令和UTF-8编码"""
    try:
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-8'))
        if process.returncode == 0:
            print("方法1 (UTF-8) 成功")
            return True
        else:
            print(f"方法1 (UTF-8) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法1 (UTF-8) 异常: {e}")
        return False

def test_clipboard_method_2(text):
    """方法2：使用Windows clip命令和GBK编码"""
    try:
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('gbk', errors='ignore'))
        if process.returncode == 0:
            print("方法2 (GBK) 成功")
            return True
        else:
            print(f"方法2 (GBK) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法2 (GBK) 异常: {e}")
        return False

def test_clipboard_method_3(text):
    """方法3：使用Windows clip命令和UTF-16-LE编码"""
    try:
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-16-le'))
        if process.returncode == 0:
            print("方法3 (UTF-16-LE) 成功")
            return True
        else:
            print(f"方法3 (UTF-16-LE) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法3 (UTF-16-LE) 异常: {e}")
        return False

def test_clipboard_method_4(text):
    """方法4：使用临时文件和clip命令"""
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            temp_file.write(text)
            temp_file_path = temp_file.name
        
        # 使用clip命令读取临时文件
        process = subprocess.Popen(['clip', '<', temp_file_path], shell=True)
        process.wait()
        
        # 删除临时文件
        os.unlink(temp_file_path)
        
        if process.returncode == 0:
            print("方法4 (临时文件) 成功")
            return True
        else:
            print(f"方法4 (临时文件) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法4 (临时文件) 异常: {e}")
        # 确保临时文件被删除
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return False

def test_clipboard_method_5(text):
    """方法5：使用echo和clip命令"""
    try:
        # 使用echo命令将文本传递给clip
        process = subprocess.Popen(f'echo "{text}" | clip', shell=True)
        process.wait()
        
        if process.returncode == 0:
            print("方法5 (echo和clip) 成功")
            return True
        else:
            print(f"方法5 (echo和clip) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法5 (echo和clip) 异常: {e}")
        return False

def test_clipboard_method_6(text):
    """方法6：使用powershell的Set-Clipboard命令"""
    try:
        # 使用PowerShell的Set-Clipboard命令
        escaped_text = text.replace('"', '`"')  # 转义引号
        process = subprocess.Popen(['powershell', '-Command', f'Set-Clipboard -Value "{escaped_text}"'])
        process.wait()
        
        if process.returncode == 0:
            print("方法6 (PowerShell Set-Clipboard) 成功")
            return True
        else:
            print(f"方法6 (PowerShell Set-Clipboard) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法6 (PowerShell Set-Clipboard) 异常: {e}")
        return False

def test_clipboard_method_7(text):
    """方法7：使用powershell的Set-Content和Get-Content"""
    try:
        # 使用PowerShell的Set-Content和Get-Content命令
        process = subprocess.Popen(['powershell', '-Command', f'Set-Content -Path "temp.txt" -Value "{text}" -Encoding UTF8; Get-Content -Path "temp.txt" -Encoding UTF8 | Set-Clipboard; Remove-Item "temp.txt"'])
        process.wait()
        
        if process.returncode == 0:
            print("方法7 (PowerShell Set-Content) 成功")
            return True
        else:
            print(f"方法7 (PowerShell Set-Content) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法7 (PowerShell Set-Content) 异常: {e}")
        return False

def test_clipboard_method_8(text):
    """方法8：使用powershell的Set-Clipboard命令，明确指定UTF-8编码"""
    try:
        # 使用PowerShell的Set-Clipboard命令，明确指定UTF-8编码
        escaped_text = text.replace('"', '`"').replace('$', '`$').replace('`', '``')  # 转义特殊字符
        process = subprocess.Popen(['powershell', '-Command', f'$text = "{escaped_text}"; $bytes = [System.Text.Encoding]::UTF8.GetBytes($text); [System.Windows.Forms.Clipboard]::SetText([System.Text.Encoding]::UTF8.GetString($bytes))'])
        process.wait()
        
        if process.returncode == 0:
            print("方法8 (PowerShell UTF-8) 成功")
            return True
        else:
            print(f"方法8 (PowerShell UTF-8) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法8 (PowerShell UTF-8) 异常: {e}")
        return False

def test_clipboard_method_9(text):
    """方法9：使用powershell的Set-Clipboard命令，明确指定Unicode编码"""
    try:
        # 使用PowerShell的Set-Clipboard命令，明确指定Unicode编码
        escaped_text = text.replace('"', '`"').replace('$', '`$').replace('`', '``')  # 转义特殊字符
        process = subprocess.Popen(['powershell', '-Command', f'$text = "{escaped_text}"; $bytes = [System.Text.Encoding]::Unicode.GetBytes($text); [System.Windows.Forms.Clipboard]::SetText([System.Text.Encoding]::Unicode.GetString($bytes))'])
        process.wait()
        
        if process.returncode == 0:
            print("方法9 (PowerShell Unicode) 成功")
            return True
        else:
            print(f"方法9 (PowerShell Unicode) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法9 (PowerShell Unicode) 异常: {e}")
        return False

def test_clipboard_method_10(text):
    """方法10：使用Windows API通过ctypes"""
    try:
        import ctypes
        from ctypes import wintypes
        
        # 定义Windows API函数
        user32 = ctypes.WinDLL('user32')
        kernel32 = ctypes.WinDLL('kernel32')
        
        # 定义常量
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        
        # 定义函数原型
        OpenClipboard = user32.OpenClipboard
        OpenClipboard.argtypes = [wintypes.HWND]
        OpenClipboard.restype = wintypes.BOOL
        
        CloseClipboard = user32.CloseClipboard
        CloseClipboard.argtypes = []
        CloseClipboard.restype = wintypes.BOOL
        
        EmptyClipboard = user32.EmptyClipboard
        EmptyClipboard.argtypes = []
        EmptyClipboard.restype = wintypes.BOOL
        
        SetClipboardData = user32.SetClipboardData
        SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        SetClipboardData.restype = wintypes.HANDLE
        
        GlobalAlloc = kernel32.GlobalAlloc
        GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        GlobalAlloc.restype = wintypes.HGLOBAL
        
        GlobalLock = kernel32.GlobalLock
        GlobalLock.argtypes = [wintypes.HGLOBAL]
        GlobalLock.restype = wintypes.LPVOID
        
        GlobalUnlock = kernel32.GlobalUnlock
        GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        GlobalUnlock.restype = wintypes.BOOL
        
        GlobalFree = kernel32.GlobalFree
        GlobalFree.argtypes = [wintypes.HGLOBAL]
        GlobalFree.restype = wintypes.HGLOBAL
        
        # 打开剪贴板
        if not OpenClipboard(None):
            print("方法10 (Windows API) 失败: 无法打开剪贴板")
            return False
        
        try:
            # 清空剪贴板
            EmptyClipboard()
            
            # 分配内存
            text_bytes = text.encode('utf-16-le') + b'\x00\x00'  # UTF-16-LE编码，以双空字节结尾
            size = len(text_bytes)
            h_mem = GlobalAlloc(GMEM_MOVEABLE, size)
            if not h_mem:
                print("方法10 (Windows API) 失败: 无法分配内存")
                return False
            
            # 锁定内存并复制数据
            mem_ptr = GlobalLock(h_mem)
            if not mem_ptr:
                GlobalFree(h_mem)
                print("方法10 (Windows API) 失败: 无法锁定内存")
                return False
            
            ctypes.memmove(mem_ptr, text_bytes, size)
            GlobalUnlock(h_mem)
            
            # 设置剪贴板数据
            if not SetClipboardData(CF_UNICODETEXT, h_mem):
                GlobalFree(h_mem)
                print("方法10 (Windows API) 失败: 无法设置剪贴板数据")
                return False
            
            print("方法10 (Windows API) 成功")
            return True
            
        finally:
            # 关闭剪贴板
            CloseClipboard()
            
    except Exception as e:
        print(f"方法10 (Windows API) 异常: {e}")
        return False

def test_clipboard_method_8(text):
    """方法8：使用powershell的Set-Clipboard命令，明确指定UTF-8编码"""
    try:
        # 使用PowerShell的Set-Clipboard命令，明确指定UTF-8编码
        escaped_text = text.replace('"', '`"').replace('$', '`$').replace('`', '``')  # 转义特殊字符
        process = subprocess.Popen(['powershell', '-Command', f'$text = "{escaped_text}"; $bytes = [System.Text.Encoding]::UTF8.GetBytes($text); [System.Windows.Forms.Clipboard]::SetText([System.Text.Encoding]::UTF8.GetString($bytes))'])
        process.wait()
        
        if process.returncode == 0:
            print("方法8 (PowerShell UTF-8) 成功")
            return True
        else:
            print(f"方法8 (PowerShell UTF-8) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法8 (PowerShell UTF-8) 异常: {e}")
        return False

def test_clipboard_method_9(text):
    """方法9：使用powershell的Set-Clipboard命令，明确指定Unicode编码"""
    try:
        # 使用PowerShell的Set-Clipboard命令，明确指定Unicode编码
        escaped_text = text.replace('"', '`"').replace('$', '`$').replace('`', '``')  # 转义特殊字符
        process = subprocess.Popen(['powershell', '-Command', f'$text = "{escaped_text}"; $bytes = [System.Text.Encoding]::Unicode.GetBytes($text); [System.Windows.Forms.Clipboard]::SetText([System.Text.Encoding]::Unicode.GetString($bytes))'])
        process.wait()
        
        if process.returncode == 0:
            print("方法9 (PowerShell Unicode) 成功")
            return True
        else:
            print(f"方法9 (PowerShell Unicode) 失败，返回码: {process.returncode}")
            return False
    except Exception as e:
        print(f"方法9 (PowerShell Unicode) 异常: {e}")
        return False

def test_clipboard_method_10(text):
    """方法10：使用Windows API通过ctypes"""
    try:
        import ctypes
        from ctypes import wintypes
        
        # 定义Windows API函数
        user32 = ctypes.WinDLL('user32')
        kernel32 = ctypes.WinDLL('kernel32')
        
        # 定义常量
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        
        # 定义函数原型
        OpenClipboard = user32.OpenClipboard
        OpenClipboard.argtypes = [wintypes.HWND]
        OpenClipboard.restype = wintypes.BOOL
        
        CloseClipboard = user32.CloseClipboard
        CloseClipboard.argtypes = []
        CloseClipboard.restype = wintypes.BOOL
        
        EmptyClipboard = user32.EmptyClipboard
        EmptyClipboard.argtypes = []
        EmptyClipboard.restype = wintypes.BOOL
        
        SetClipboardData = user32.SetClipboardData
        SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        SetClipboardData.restype = wintypes.HANDLE
        
        GlobalAlloc = kernel32.GlobalAlloc
        GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        GlobalAlloc.restype = wintypes.HGLOBAL
        
        GlobalLock = kernel32.GlobalLock
        GlobalLock.argtypes = [wintypes.HGLOBAL]
        GlobalLock.restype = wintypes.LPVOID
        
        GlobalUnlock = kernel32.GlobalUnlock
        GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        GlobalUnlock.restype = wintypes.BOOL
        
        GlobalFree = kernel32.GlobalFree
        GlobalFree.argtypes = [wintypes.HGLOBAL]
        GlobalFree.restype = wintypes.HGLOBAL
        
        # 打开剪贴板
        if not OpenClipboard(None):
            print("方法10 (Windows API) 失败: 无法打开剪贴板")
            return False
        
        try:
            # 清空剪贴板
            EmptyClipboard()
            
            # 分配内存
            text_bytes = text.encode('utf-16-le') + b'\x00\x00'  # UTF-16-LE编码，以双空字节结尾
            size = len(text_bytes)
            h_mem = GlobalAlloc(GMEM_MOVEABLE, size)
            if not h_mem:
                print("方法10 (Windows API) 失败: 无法分配内存")
                return False
            
            # 锁定内存并复制数据
            mem_ptr = GlobalLock(h_mem)
            if not mem_ptr:
                GlobalFree(h_mem)
                print("方法10 (Windows API) 失败: 无法锁定内存")
                return False
            
            ctypes.memmove(mem_ptr, text_bytes, size)
            GlobalUnlock(h_mem)
            
            # 设置剪贴板数据
            if not SetClipboardData(CF_UNICODETEXT, h_mem):
                GlobalFree(h_mem)
                print("方法10 (Windows API) 失败: 无法设置剪贴板数据")
                return False
            
            print("方法10 (Windows API) 成功")
            return True
            
        finally:
            # 关闭剪贴板
            CloseClipboard()
            
    except Exception as e:
        print(f"方法10 (Windows API) 异常: {e}")
        return False

def main():
    # 测试文本
    test_text1 = "这是一段中文测试文本"
    test_text2 = "按顺序列出刚刚的所有对应的题号及答案，区分单题和共用题干的多题，格式参考：\n1.B\n2.D\n3.D\n4-5.A，B\n6-8.A，B，C"
    test_text3 = "（1）（禁搜索＋禁深度思考）按顺序简要回答以下题目，区分单题和共用题干的多题，勤搜索保证正确率"
    
    test_texts = [
        ("简单中文文本", test_text1),
        ("带格式的中文文本", test_text2),
        ("AI提示词文本", test_text3)
    ]
    
    # 测试方法列表
    test_methods = [
        test_clipboard_method_1,
        test_clipboard_method_2,
        test_clipboard_method_3,
        test_clipboard_method_4,
        test_clipboard_method_5,
        test_clipboard_method_6,
        test_clipboard_method_7,
        test_clipboard_method_8,
        test_clipboard_method_9,
        test_clipboard_method_10
    ]
    
    # 对每个测试文本运行所有测试方法
    for text_name, text in test_texts:
        print(f"\n{'='*50}")
        print(f"测试文本: {text_name}")
        print(f"内容: {text}")
        print(f"{'='*50}")
        
        successful_methods = []
        
        for method in test_methods:
            print(f"\n测试 {method.__name__}:")
            if method(text):
                successful_methods.append(method.__name__)
        
        print(f"\n成功的方法: {', '.join(successful_methods) if successful_methods else '无'}")
        
        # 等待用户确认测试结果
        input("请粘贴测试结果并按Enter键继续下一个测试...")

if __name__ == "__main__":
    main()