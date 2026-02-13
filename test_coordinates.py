"""
좌표 설정 테스트 도구
설정된 좌표로 실제 클릭해보고 올바른지 확인
"""
import pyautogui
import time
from rl.config import (
    CHAT_OUTPUT_COORD, CHAT_INPUT_COORD,
    CHAT_OUTPUT_COORD_RATIO, CHAT_INPUT_COORD_RATIO,
    USE_RELATIVE_COORDS
)

# Fail-safe 비활성화 (테스트용)
pyautogui.FAILSAFE = False

def get_absolute_coords(coord_type='output'):
    """비율 또는 절대 좌표를 실제 픽셀 좌표로 변환"""
    if USE_RELATIVE_COORDS:
        screen_width, screen_height = pyautogui.size()

        if coord_type == 'output':
            x_ratio, y_ratio = CHAT_OUTPUT_COORD_RATIO
        else:
            x_ratio, y_ratio = CHAT_INPUT_COORD_RATIO

        x = int(screen_width * x_ratio)
        y = int(screen_height * y_ratio)

        return (x, y)
    else:
        if coord_type == 'output':
            return CHAT_OUTPUT_COORD
        else:
            return CHAT_INPUT_COORD

def main():
    screen_width, screen_height = pyautogui.size()

    print("=" * 70)
    print("좌표 설정 테스트 도구")
    print("=" * 70)
    print(f"\n현재 화면 해상도: {screen_width} x {screen_height}")
    print(f"좌표 모드: {'비율 기반' if USE_RELATIVE_COORDS else '절대 좌표'}")
    print()

    # 채팅 출력창 좌표
    output_coords = get_absolute_coords('output')
    print(f"채팅 출력창 좌표:")
    if USE_RELATIVE_COORDS:
        print(f"  비율: {CHAT_OUTPUT_COORD_RATIO}")
    print(f"  실제 좌표: {output_coords}")

    # 채팅 입력창 좌표
    input_coords = get_absolute_coords('input')
    print(f"\n채팅 입력창 좌표:")
    if USE_RELATIVE_COORDS:
        print(f"  비율: {CHAT_INPUT_COORD_RATIO}")
    print(f"  실제 좌표: {input_coords}")

    print("\n" + "=" * 70)
    print("3초 후 채팅 출력창 위치를 클릭합니다.")
    print("카카오톡 채팅방을 열어두세요!")
    print("=" * 70)

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # 채팅 출력창 클릭
    print(f"\n✓ 채팅 출력창 클릭: {output_coords}")
    pyautogui.click(*output_coords)

    # 마우스 위치 표시
    time.sleep(0.5)
    actual_pos = pyautogui.position()
    print(f"  마우스 실제 위치: {actual_pos}")

    # 입력창 테스트
    print("\n3초 후 채팅 입력창 위치를 클릭합니다.")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print(f"\n✓ 채팅 입력창 클릭: {input_coords}")
    pyautogui.click(*input_coords)

    time.sleep(0.5)
    actual_pos = pyautogui.position()
    print(f"  마우스 실제 위치: {actual_pos}")

    print("\n" + "=" * 70)
    print("클릭한 위치가 올바른지 확인하세요!")
    print("잘못된 경우 get_coordinates_pyautogui.py로 좌표를 다시 측정하세요.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
