"""Capture real public pages, including browser chrome for the container page."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools'))
from playwright.sync_api import sync_playwright
from PIL import Image


def capture_browser_window(title, destination):
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    user32.GetWindowDC.restype = wintypes.HDC
    user32.GetWindowDC.argtypes = [wintypes.HWND]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi32.SelectObject.restype = wintypes.HANDLE
    gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]
    gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]
    user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    gdi32.DeleteObject.argtypes = [wintypes.HANDLE]
    windows = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @callback_type
    def callback(hwnd, _):
        text = ctypes.create_unicode_buffer(1024)
        user32.GetWindowTextW(hwnd, text, 1024)
        if title in text.value and user32.IsWindowVisible(hwnd):
            windows.append(hwnd)
        return True

    user32.EnumWindows(callback, 0)
    if not windows:
        raise RuntimeError('Could not locate the portfolio browser window')
    hwnd = windows[0]
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width, height = rect.right - rect.left, rect.bottom - rect.top
    dc = user32.GetWindowDC(hwnd)
    memory = gdi32.CreateCompatibleDC(dc)
    bitmap = gdi32.CreateCompatibleBitmap(dc, width, height)
    previous = gdi32.SelectObject(memory, bitmap)
    try:
        if not user32.PrintWindow(hwnd, memory, 2):
            raise RuntimeError('Windows could not capture the actual browser window')
        header = bytearray(40)
        import struct
        struct.pack_into('<IiiHHIIiiII', header, 0, 40, width, -height, 1, 32, 0, width * height * 4, 0, 0, 0, 0)
        info = ctypes.create_string_buffer(bytes(header))
        pixels = ctypes.create_string_buffer(width * height * 4)
        if not gdi32.GetDIBits(memory, bitmap, 0, height, pixels, info, 0):
            raise RuntimeError('Could not read browser pixels')
        Image.frombytes('RGB', (width, height), pixels.raw, 'raw', 'BGRX').save(destination)
    finally:
        gdi32.SelectObject(memory, previous)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(memory)
        user32.ReleaseDC(hwnd, dc)


def main():
    evidence = ROOT / 'evidence'
    evidence.mkdir(exist_ok=True)
    state_path = evidence / 'remote-state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    repo = 'https://github.com/MahaIshaq04/devops-a2-fa23-bai-037'
    targets = {
        'commit-history': repo + '/commits/main/',
        'merged-pr': state.get('feature_pr_url'),
        'dockerhub-tags': 'https://hub.docker.com/r/mahaishaq04/devops-a2/tags',
        'failed-actions': state.get('deliberate_failed_run_url'),
        'passed-actions': state.get('successful_main_run_url'),
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
            headless=False, args=['--window-size=1440,1100', '--force-device-scale-factor=1'])
        context = browser.new_context(viewport={'width': 1400, 'height': 960}, device_scale_factor=1)
        page = context.new_page()
        try:
            response = page.goto('http://localhost:8080/', wait_until='networkidle', timeout=45000)
            if response.status != 200 or 'fa23-bai-037' not in page.inner_text('body'):
                raise RuntimeError('Container page did not load correctly')
            page.screenshot(path=str(evidence / 'container-page.png'), full_page=True)
            page.wait_for_timeout(1500)
            capture_browser_window('Maha Ishaq', evidence / 'container-browser.png')
            print('Captured container page and real browser window with address bar.')
            for name, url in targets.items():
                if not url:
                    continue
                try:
                    response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    page.wait_for_timeout(4000)
                    page.screenshot(path=str(evidence / (name + '.png')), full_page=False)
                    print(name, 'HTTP', response.status, page.title())
                except Exception as exc:
                    print('Could not capture', name, type(exc).__name__)
        finally:
            browser.close()


if __name__ == '__main__':
    main()
