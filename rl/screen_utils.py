"""
화면 해상도 및 좌표 처리 유틸리티
DPI 스케일링을 올바르게 처리
"""
import platform
import ctypes

def get_true_screen_resolution():
    """
    DPI 스케일링을 고려한 실제 물리 해상도 반환
    Windows에서 125%, 150% 등의 스케일링이 적용되어도 올바른 해상도 반환
    """
    if platform.system() != 'Windows':
        import pyautogui
        return pyautogui.size()

    try:
        # DPI Aware 설정 (고해상도 화면 인식)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

    user32 = ctypes.windll.user32

    # 가상 화면 크기 (모든 모니터 포함, 물리 픽셀)
    width = user32.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
    height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN

    return (width, height)

def get_dpi_scale():
    """
    현재 DPI 스케일 배율 반환 (1.0 = 100%, 1.25 = 125%, 1.5 = 150%)
    """
    if platform.system() != 'Windows':
        return 1.0

    try:
        user32 = ctypes.windll.user32
        dpi = user32.GetDpiForSystem()
        return dpi / 96.0
    except:
        return 1.0

if __name__ == "__main__":
    width, height = get_true_screen_resolution()
    scale = get_dpi_scale()
    print(f"실제 물리 해상도: {width} x {height}")
    print(f"DPI 스케일: {scale:.2f}x ({int(scale * 100)}%)")
