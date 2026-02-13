"""
pyautogui용 마우스 좌표 확인 도구
비율 기반 좌표 설정 지원 (원격 데스크톱 환경에서 해상도 변경 대응)
DPI 스케일링(125%, 150% 등) 자동 처리
Ctrl+C를 누르면 종료됩니다.
"""
import pyautogui
import time
import sys
from rl.screen_utils import get_true_screen_resolution, get_dpi_scale

# DPI 스케일링을 고려한 실제 물리 해상도 확인
screen_width, screen_height = get_true_screen_resolution()
dpi_scale = get_dpi_scale()

print("=" * 70)
print("pyautogui 마우스 좌표 확인 도구 (DPI 스케일링 지원)")
print("=" * 70)
print(f"\n실제 물리 해상도: {screen_width} x {screen_height}")
print(f"DPI 스케일링: {int(dpi_scale * 100)}% ({dpi_scale:.2f}x)")
print("\n사용 방법:")
print("1. 카카오톡 게임봇 채팅방을 엽니다")
print("2. 마우스를 '채팅 메시지 출력 영역' 중앙에 올립니다")
print("3. 표시된 비율(ratio)을 CHAT_OUTPUT_COORD_RATIO에 입력합니다")
print("4. 마우스를 '채팅 입력창' 중앙에 올립니다")
print("5. 표시된 비율(ratio)을 CHAT_INPUT_COORD_RATIO에 입력합니다")
print("\n💡 DPI 스케일링이 자동으로 고려되므로 정확한 비율이 표시됩니다!")
print("\nCtrl+C를 누르면 종료됩니다.\n")
print("=" * 70)

try:
    while True:
        x, y = pyautogui.position()
        # 비율 계산 (소수점 3자리) - 실제 물리 해상도 기준
        x_ratio = x / screen_width
        y_ratio = y / screen_height

        print(f"\r좌표: ({x:4d}, {y:4d}) | 비율: ({x_ratio:.3f}, {y_ratio:.3f})  (Ctrl+C로 종료)",
              end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n프로그램을 종료합니다.")
    print("\nconfig.py에 다음과 같이 입력하세요:")
    print("CHAT_OUTPUT_COORD_RATIO = (x비율, y비율)  # 채팅 출력창")
    print("CHAT_INPUT_COORD_RATIO = (x비율, y비율)   # 채팅 입력창")
    print("\n✅ 이제 원격 데스크톱에서도 자동으로 정확한 좌표로 동작합니다!")
    sys.exit(0)
