"""
마우스 좌표를 실시간으로 확인하는 도구
ESC 키를 누르면 종료됩니다.
"""
from pynput import mouse, keyboard
import time

current_position = (0, 0)
running = True

def on_move(x, y):
    global current_position
    current_position = (x, y)

def on_press(key):
    global running
    if key == keyboard.Key.esc:
        print("\n프로그램을 종료합니다.")
        running = False
        return False

def display_coordinates():
    print("=" * 60)
    print("마우스 좌표 확인 도구")
    print("=" * 60)
    print("\n사용 방법:")
    print("1. 카카오톡 게임봇 채팅방을 엽니다")
    print("2. 마우스를 '채팅 메시지 출력 영역' 중앙에 올립니다")
    print("3. 표시된 좌표를 CHAT_OUTPUT_COORD에 입력합니다")
    print("4. 마우스를 '채팅 입력창' 중앙에 올립니다")
    print("5. 표시된 좌표를 CHAT_INPUT_COORD에 입력합니다")
    print("\nESC 키를 누르면 종료됩니다.\n")
    print("=" * 60)

    mouse_listener = mouse.Listener(on_move=on_move)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    try:
        while running:
            x, y = current_position
            print(f"\r현재 마우스 좌표: X = {x:4d}, Y = {y:4d}  (ESC로 종료)", end="", flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    finally:
        mouse_listener.stop()
        keyboard_listener.stop()

if __name__ == "__main__":
    display_coordinates()
