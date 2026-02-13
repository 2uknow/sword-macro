"""
화면 정보 확인 도구
듀얼 모니터 환경에서 pyautogui가 인식하는 해상도 확인
"""
import pyautogui
import platform

print("=" * 70)
print("화면 정보 확인")
print("=" * 70)

# 기본 화면 정보
screen_width, screen_height = pyautogui.size()
print(f"\npyautogui.size(): {screen_width} x {screen_height}")

# 플랫폼별 추가 정보
if platform.system() == 'Windows':
    try:
        import ctypes
        user32 = ctypes.windll.user32

        # 가상 화면 크기 (모든 모니터 포함)
        virtual_width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        virtual_height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        print(f"가상 화면 크기 (모든 모니터): {virtual_width} x {virtual_height}")

        # 주 모니터 크기
        primary_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        primary_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        print(f"주 모니터 크기: {primary_width} x {primary_height}")

        # DPI 스케일링
        try:
            user32.SetProcessDPIAware()
            dpi = user32.GetDpiForSystem()
            scale = dpi / 96.0
            print(f"DPI 스케일링: {scale:.2f}x ({dpi} DPI)")
        except:
            print("DPI 정보를 가져올 수 없습니다")

    except Exception as e:
        print(f"Windows 추가 정보를 가져올 수 없습니다: {e}")

# 현재 마우스 위치
current_x, current_y = pyautogui.position()
print(f"\n현재 마우스 위치: ({current_x}, {current_y})")

# 설정된 좌표 분석
print("\n" + "=" * 70)
print("config.py의 좌표 분석")
print("=" * 70)

from rl.config import CHAT_OUTPUT_COORD, CHAT_OUTPUT_COORD_RATIO

absolute_x, absolute_y = CHAT_OUTPUT_COORD
ratio_x, ratio_y = CHAT_OUTPUT_COORD_RATIO

print(f"\n절대 좌표: ({absolute_x}, {absolute_y})")
print(f"비율 좌표: ({ratio_x}, {ratio_y})")

# 비율로 계산한 픽셀 좌표
calc_x = int(screen_width * ratio_x)
calc_y = int(screen_height * ratio_y)
print(f"\n비율로 계산한 좌표: ({calc_x}, {calc_y})")
print(f"절대 좌표와의 차이: ({calc_x - absolute_x}, {calc_y - absolute_y})")

# 역산: 절대 좌표가 어떤 해상도 기준인지 추정
print("\n" + "=" * 70)
print("절대 좌표가 의미하는 해상도 추정")
print("=" * 70)

# 듀얼 모니터 전체 (3840*2 x 2160)
dual_width = 7680
dual_height = 2160
estimated_ratio_x = absolute_x / dual_width
estimated_ratio_y = absolute_y / dual_height
print(f"\n듀얼 모니터 전체 ({dual_width}x{dual_height}) 기준:")
print(f"  비율: ({estimated_ratio_x:.3f}, {estimated_ratio_y:.3f})")

# 단일 모니터 (3840 x 2160) - 두 번째 모니터 기준
single_width = 3840
single_height = 2160
second_monitor_x = absolute_x - 3840  # 두 번째 모니터 시작점
if second_monitor_x >= 0:
    estimated_ratio_x_single = second_monitor_x / single_width
    estimated_ratio_y_single = absolute_y / single_height
    print(f"\n두 번째 모니터 ({single_width}x{single_height}) 기준:")
    print(f"  두 번째 모니터 내 좌표: ({second_monitor_x}, {absolute_y})")
    print(f"  비율: ({estimated_ratio_x_single:.3f}, {estimated_ratio_y_single:.3f})")

print("\n" + "=" * 70)
print("권장 사항:")
print("=" * 70)
print("\n1. pyautogui.size()가 반환하는 값을 확인하세요")
print(f"   현재: {screen_width} x {screen_height}")
print(f"   예상: 7680 x 2160 (듀얼 모니터 전체)")
print("\n2. 만약 다르다면, get_coordinates_pyautogui.py로 좌표를 다시 측정하세요")
print("\n3. 카카오톡을 열고 마우스를 올려서 좌표를 확인하세요")
print("   (이 스크립트를 실행한 채로 카카오톡에 마우스를 올리면 실시간 좌표 표시)")

print("\n" + "=" * 70)
