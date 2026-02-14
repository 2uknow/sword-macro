from pynput import keyboard
import time
import pyperclip
import re
import threading
import platform
import argparse
import os
import subprocess
from datetime import datetime, timedelta
import pyautogui
from rl.inference import SwordAI
from rl.config import (
    CHAT_OUTPUT_COORD, CHAT_INPUT_COORD,
    CHAT_OUTPUT_COORD_RATIO, CHAT_INPUT_COORD_RATIO,
    USE_RELATIVE_COORDS, ACTION_DELAY, MAX_LEVEL_FOR_ENHANCE,
    DEBUG_MODE, COORD_PROFILES, DEFAULT_PROFILE
)
from rl.screen_utils import get_true_screen_resolution

# PyAutoGUI 설정
# 원격 데스크톱 환경에서 해상도 변경 시 fail-safe 오작동을 방지
# 대신 좌표 범위 검사를 직접 구현
pyautogui.FAILSAFE = False  # fail-safe 비활성화
pyautogui.PAUSE = 0.02  # 각 pyautogui 명령 후 짧은 대기 (기존 0.05)

# Detect platform and set modifier key
if platform.system() == 'Darwin':  # macOS
    MODIFIER_KEY = keyboard.Key.cmd
else:  # Windows and Linux
    MODIFIER_KEY = keyboard.Key.ctrl

is_running = True
pressed_keys = set()
controller = keyboard.Controller()
ai = SwordAI()

running_mode = None  # 'ai' or 'heuristic' or None
fail_count = 0
prev_text = ""
same_message_count = 0  # 같은 메시지가 연속으로 나온 횟수
action_lock = threading.Lock()  # 동시 실행 방지용 Lock

# 목표 달성 후 재시작용
_goal_reached_event = threading.Event()
_goal_reached_mode = [None]

# 통계 추적
start_fund = None
current_fund = None  # 마지막으로 알려진 골드
max_level_achieved = 0
total_enhances = 0
total_sells = 0
total_sell_amount = 0
level_counts = {}  # 레벨별 최종 달성 횟수 {10: 5, 11: 3, ...}
current_sword_max = 0  # 현재 검의 최고 레벨
prev_level = 0  # 이전 레벨 (검 교체 감지용)
_sell_item_keywords = []  # --sell-items로 설정, 아이템 이름에 키워드 포함 시 강제 판매
_keep_item_keywords = []  # --keep-items로 설정, 이 키워드 포함 시 판매 안 함 (sell보다 우선)
_filter_sell_pending = False  # 필터 판매 후 봇 응답 대기 중
_continue_past_goal = False  # 목표 달성 후 계속 강화 모드

def _reset_stats():
    global fail_count, prev_text, same_message_count
    global start_fund, current_fund, max_level_achieved
    global total_enhances, total_sells, total_sell_amount
    global level_counts, current_sword_max, prev_level
    global _filter_sell_pending, _continue_past_goal

    fail_count = 0
    prev_text = ""
    same_message_count = 0
    _filter_sell_pending = False
    _continue_past_goal = False
    start_fund = None
    current_fund = None
    max_level_achieved = 0
    total_enhances = 0
    total_sells = 0
    total_sell_amount = 0
    level_counts = {}
    current_sword_max = 0
    prev_level = 0

def worker_loop():
    global running_mode, _filter_sell_pending
    while True:
        try:
            if _goal_reached_event.is_set():
                try:
                    choice = input().strip().lower()
                except EOFError:
                    print("(background mode: auto-restart in 5s)")
                    time.sleep(5)
                    choice = ""

                if choice == 'c':
                    # 현재 상태 유지하고 계속 강화
                    _continue_past_goal = True
                    print("")
                    print("=" * 60)
                    print("  >>> 목표 초과 강화 모드! 계속 진행...")
                    print("=" * 60)
                    print("")
                else:
                    # 초기화 후 재시작
                    _reset_stats()
                    print("")
                    print("=" * 60)
                    print("  >>> Stats reset! Restarting...")
                    print("=" * 60)
                    print("")
                running_mode = _goal_reached_mode[0]
                _goal_reached_event.clear()
                continue

            if running_mode == 'ai':
                act_inference('ai')
                if _filter_sell_pending:
                    time.sleep(2.5)
                    _filter_sell_pending = False
                else:
                    time.sleep(ACTION_DELAY)
            elif running_mode == 'heuristic':
                act_inference('heuristic')
                if _filter_sell_pending:
                    time.sleep(2.5)
                    _filter_sell_pending = False
                else:
                    time.sleep(ACTION_DELAY)
            else:
                time.sleep(0.1)
        except pyautogui.FailSafeException:
            # Fail-safe 예외는 무시하고 계속 진행
            print("\n⚠️ Fail-safe 감지 - 잠시 대기 후 재시도")
            time.sleep(2.0)
            continue
        except Exception as e:
            # 기타 예외 발생 시 로그만 남기고 계속 진행
            print(f"\n⚠️ 오류 발생: {e}")
            print("5초 대기 후 재시도...")
            time.sleep(5.0)
            continue

t = threading.Thread(target=worker_loop, daemon=True)
t.start()

def _get_absolute_coords(coord_type='output'):
    """
    비율 또는 절대 좌표를 실제 픽셀 좌표로 변환
    해상도가 변경되어도 자동으로 올바른 좌표 계산
    DPI 스케일링(125%, 150% 등)을 올바르게 처리
    """
    if USE_RELATIVE_COORDS:
        # DPI 스케일링을 고려한 실제 물리 해상도 가져오기
        screen_width, screen_height = get_true_screen_resolution()

        if coord_type == 'output':
            x_ratio, y_ratio = CHAT_OUTPUT_COORD_RATIO
        else:  # 'input'
            x_ratio, y_ratio = CHAT_INPUT_COORD_RATIO

        # 비율을 픽셀로 변환
        x = int(screen_width * x_ratio)
        y = int(screen_height * y_ratio)

        return (x, y)
    else:
        # 절대 좌표 사용
        if coord_type == 'output':
            return CHAT_OUTPUT_COORD
        else:
            return CHAT_INPUT_COORD

def _click_mouse(x, y):
    """
    안전하게 마우스 클릭 수행
    화면 범위를 벗어나는 좌표는 자동으로 보정
    """
    try:
        # DPI 스케일링을 고려한 실제 화면 크기 확인
        screen_width, screen_height = get_true_screen_resolution()

        # 원본 좌표 저장 (디버그용)
        original_x, original_y = x, y

        # 좌표가 화면 범위 내에 있는지 확인 및 보정
        # 화면 가장자리(fail-safe 영역) 50px은 피함
        safe_margin = 50
        x = max(safe_margin, min(x, screen_width - safe_margin))
        y = max(safe_margin, min(y, screen_height - safe_margin))

        # 디버그 모드: 클릭 좌표 출력
        if DEBUG_MODE:
            if (x, y) != (original_x, original_y):
                print(f"\n[DEBUG] 좌표 보정: ({original_x}, {original_y}) → ({x}, {y})")
            else:
                print(f"\n[DEBUG] 클릭: ({x}, {y}) | 화면: {screen_width}x{screen_height}")

        # 클릭 수행
        pyautogui.click(x, y)
        time.sleep(0.05)
    except Exception as e:
        # 클릭 실패 시 경고만 출력하고 계속 진행
        print(f"\n⚠️ 클릭 실패 ({x}, {y}): {e}")
        time.sleep(0.5)  # 잠시 대기 후 재시도

def _copy_message():
    # 채팅창 클릭 (현재 해상도에 맞춰 자동 계산)
    output_coords = _get_absolute_coords('output')
    _click_mouse(*output_coords)

    # 맨 아래로 스크롤 + 전체 선택 + 복사를 빠르게 연속 실행
    controller.press(keyboard.Key.end)
    controller.release(keyboard.Key.end)
    time.sleep(0.02)

    # Ctrl+A → Ctrl+C 연속 실행
    controller.press(MODIFIER_KEY)
    controller.press('a')
    controller.release('a')
    controller.press('c')
    controller.release('c')
    controller.release(MODIFIER_KEY)
    time.sleep(0.03)  # 클립보드 반영 대기

    text = pyperclip.paste()
    return text

def _safe_paste(command):
    """클립보드에 명령어를 설정하고 검증 후 붙여넣기 (Ctrl+C 잔여 이벤트 방지)"""
    for attempt in range(5):
        pyperclip.copy(command)
        time.sleep(0.05)
        if pyperclip.paste() == command:
            break
        # 클립보드가 Ctrl+C 잔여 이벤트로 덮어씌워짐 - 재시도
        if attempt < 4:
            time.sleep(0.05)

    controller.press(MODIFIER_KEY)
    controller.press('v')
    time.sleep(0.05)
    controller.release('v')
    controller.release(MODIFIER_KEY)

def _parse_message(message):
    global fail_count

    # 속보 메시지 확인 (전체 메시지에서 먼저 확인)
    is_breaking_news = '🚨[속보]🚨' in message and '강화에 성공' in message

    # 최근 2개의 [플레이봇] 메시지를 합쳐서 파싱 (골드와 레벨이 다른 메시지에 있을 수 있음)
    bot_messages = message.split('[플레이봇]')
    if len(bot_messages) > 2:
        # 마지막 2개 메시지를 합침
        combined_message = '[플레이봇]'.join(bot_messages[-2:])
    elif len(bot_messages) > 1:
        combined_message = bot_messages[-1]
    else:
        combined_message = message

    # 마지막 메시지가 "강화 중이니 잠깐 기다리도록"이면 fail_count 변경 안 함
    last_msg = bot_messages[-1] if len(bot_messages) > 1 else message
    is_wait_message = '강화 중이니 잠깐 기다리도록' in last_msg

    # 강화 결과 파싱
    enhance_pattern = re.findall(r'강화 (\w+)', combined_message)
    result = enhance_pattern[0] if enhance_pattern else None

    if not is_wait_message:  # 대기 메시지면 fail_count 변경 안 함
        if result == '유지':
            fail_count += 1
        elif '파괴' in combined_message or '산산조각' in combined_message:
            fail_count = 0
            result = '파괴'
        elif is_breaking_news:
            fail_count = 0
            result = '성공'
        elif result == '성공':
            fail_count = 0
        # else: 파싱 실패 시 fail_count 유지

    # 골드 파싱 (전체 메시지에서 가장 마지막 골드 찾기)
    gold_pattern = re.findall(r'남은\s*골드:\s*([\d,]+)\s*G', combined_message)
    if not gold_pattern:
        gold_pattern = re.findall(r'(?:현재\s*보유|보유)\s*골드:\s*([\d,]+)\s*G', combined_message)
    fund = int(gold_pattern[-1].replace(',', '')) if gold_pattern else None  # 마지막 골드 사용

    # 레벨 파싱
    # 1. 속보 메시지 (우선순위 최상 - 전체 메시지에서 찾기)
    if is_breaking_news:
        level_pattern = re.findall(r'\[?\+(\d+)\]?', message)  # 전체 메시지에서 찾기
        level = int(level_pattern[-1]) if level_pattern else None
        # 처음 강화 성공(1강)일 때만 속보 출력
        if level == 1:
            print(f"🚨 속보 감지: {level}강 성공!")
    # 2. 판매 후 새 검 획득
    elif '새로운 검 획득:' in combined_message:
        new_sword = re.findall(r'새로운 검 획득:.*?\[?\+(\d+)\]?', combined_message)
        level = int(new_sword[-1]) if new_sword else 0
        fail_count = 0  # 새 검이니 실패 카운트 리셋
    # 3. "지급되었습니다" (판매 후)
    elif '지급되었습니다' in combined_message:
        after_give = combined_message.split('지급되었습니다')[0]
        level_pattern = re.findall(r'\[?\+(\d+)\]?', after_give)
        level = int(level_pattern[-1]) if level_pattern else 0
        fail_count = 0  # 새 검이니 실패 카운트 리셋
    # 4. 일반 강화 결과
    else:
        level_pattern = re.findall(r'\[?\+(\d+)\]?', combined_message)
        level = int(level_pattern[-1]) if level_pattern else (0 if result == '파괴' else None)

    return fund, level

def act_enhance():
    global total_enhances
    with action_lock:
        # 클립보드 백업
        old_clipboard = pyperclip.paste()

        # 카카오톡 입력창 클릭 (포커스, 현재 해상도에 맞춰 자동 계산)
        input_coords = _get_absolute_coords('input')
        _click_mouse(*input_coords)
        time.sleep(0.1)

        _safe_paste('/강화')
        time.sleep(0.2)

        # 클립보드 복원
        pyperclip.copy(old_clipboard)

        pyautogui.press('enter')
        time.sleep(0.05)
        pyautogui.press('enter')
        time.sleep(0.1)

        total_enhances += 1
        print(f"⚔️ 강화 시도 (총 {total_enhances}회)")

def act_sell():
    global total_sells
    with action_lock:
        # 클립보드 백업
        old_clipboard = pyperclip.paste()

        # 카카오톡 입력창 클릭 (포커스, 현재 해상도에 맞춰 자동 계산)
        input_coords = _get_absolute_coords('input')
        _click_mouse(*input_coords)
        time.sleep(0.1)

        _safe_paste('/판매')
        time.sleep(0.2)

        # 클립보드 복원
        pyperclip.copy(old_clipboard)

        pyautogui.press('enter')
        time.sleep(0.05)
        pyautogui.press('enter')
        time.sleep(0.1)

        total_sells += 1
        print(f"💰 판매 시도 (총 {total_sells}회)")

def send_congratulation_message(level):
    """목표 레벨 달성 시 축하 메시지를 채팅에 전송"""
    global running_mode
    with action_lock:
        # 클립보드 백업
        old_clipboard = pyperclip.paste()

        # 카카오톡 입력창 클릭 (포커스, 현재 해상도에 맞춰 자동 계산)
        input_coords = _get_absolute_coords('input')
        _click_mouse(*input_coords)
        time.sleep(0.1)

        # 축하 메시지 작성
        congratulation_msg = f"🎉🎊 축하합니다! +{level} 강화 목표 달성! 🎊🎉"
        _safe_paste(congratulation_msg)
        time.sleep(0.2)

        # 클립보드 복원
        pyperclip.copy(old_clipboard)

        # 메시지 전송
        pyautogui.press('enter')
        time.sleep(0.1)

        print(f"🎉 목표 달성! +{level} 강화 완료! 자동 모드 중지")
        print("")
        print("Enter = 초기화 재시작 / c = 계속 강화 / F5 or ESC = 종료")
        previous_mode = running_mode
        running_mode = None  # 자동 모드 중지
        _goal_reached_mode[0] = previous_mode
        _goal_reached_event.set()

def act_inference(mode='ai'):
    # 메시지 복사 및 파싱은 lock 안에서
    with action_lock:
        global prev_text, same_message_count, start_fund, max_level_achieved, current_fund
        global _filter_sell_pending
        text = _copy_message()

        force_enhance = False
        if prev_text == text:
            same_message_count += 1

            print(f"⏳ 봇 응답 대기 중... ({same_message_count}/10)")

            # 봇 응답 대기 (최대 3번 재확인)
            for retry in range(3):
                time.sleep(1.0)  # 1초 대기
                text = _copy_message()
                if text != prev_text:
                    print(f"✅ 새 메시지 확인 (재시도 {retry + 1}회)")
                    same_message_count = 0
                    prev_text = text
                    break

            # 3번 확인해도 같은 메시지면
            if prev_text == text:
                if same_message_count >= 10:
                    print("⚠️ 봇 응답 없음, 대기")
                    return
                else:
                    force_enhance = True
        else:
            same_message_count = 0  # 새 메시지면 카운터 리셋
            prev_text = text

        fund, level = _parse_message(text)

        # 골드가 없으면 이전 값 사용 (속보 메시지 등)
        if fund is None and current_fund is not None:
            fund = current_fund
        elif fund is not None:
            current_fund = fund

        # 시작 자금 기록
        if start_fund is None and fund is not None:
            start_fund = fund

        # 마지막 봇 메시지에서 특수 메시지 감지
        bot_messages = text.split('[플레이봇]')
        last_bot_message = bot_messages[-1] if len(bot_messages) > 1 else text

        # 골드 부족 메시지 감지 (마지막 메시지에서만)
        is_out_of_gold = ('골드가 부족해' in last_bot_message or '💸 필요 골드:' in last_bot_message)

        # 0강 판매 불가 메시지 감지 (이미 판매한 상태)
        is_zero_sword = '0강검은 가치가 없어서' in last_bot_message or '판매할 수 없다네' in last_bot_message

        # 최고 레벨 갱신 + 레벨별 달성 카운트
        global prev_level, level_counts, current_sword_max
        if level is not None:
            if level > max_level_achieved:
                max_level_achieved = level
                print(f"🔥 신기록! {max_level_achieved}강 달성!")

            # 검이 바뀌었는지 감지 (레벨이 크게 떨어지면 = 판매/파괴)
            if level < prev_level - 1:
                # 이전 검의 최고 레벨 카운트 (1강 이상)
                if current_sword_max >= 1:
                    level_counts[current_sword_max] = level_counts.get(current_sword_max, 0) + 1
                current_sword_max = level  # 새 검으로 리셋
            else:
                # 현재 검의 최고 레벨 갱신
                if level > current_sword_max:
                    current_sword_max = level

            prev_level = level

        # 목표 레벨 달성 체크 (계속 강화 모드면 스킵)
        if level is not None and level >= MAX_LEVEL_FOR_ENHANCE and not _continue_past_goal:
            global running_mode
            previous_mode = running_mode
            running_mode = None
            profit = fund - start_fund if (start_fund and fund) else 0
            print("="*60)
            print(f"🎉 목표 달성! {MAX_LEVEL_FOR_ENHANCE}강에 도달했습니다! 🎉")
            print(f"📊 최종 통계:")
            if fund and start_fund:
                print(f"   시작 골드: {start_fund:,}G | 현재 골드: {fund:,}G")
                print(f"   순이익: {profit:+,}G ({(profit/start_fund*100):+.1f}%)")
            print(f"   총 강화: {total_enhances}회 | 총 판매: {total_sells}회")
            print(f"   최고 레벨: {max_level_achieved}강")
            if level_counts:
                stats = " | ".join([f"{lv}강:{cnt}회" for lv, cnt in sorted(level_counts.items())])
                print(f"   레벨별 달성: {stats}")
            print("="*60)
            print("")
            print("Enter = 초기화 재시작 / c = 계속 강화 / F5 or ESC = 종료")
            _goal_reached_mode[0] = previous_mode
            _goal_reached_event.set()
            return

        # 0강 판매 불가 메시지면 무조건 강화 (이미 판매한 상태)
        if is_zero_sword:
            print("🔄 0강 검 감지 - 무조건 강화")
            inference_result = 0
            # 필터 키워드 매칭 시 강화 후 봇 응답 대기 (연속 강화 방지)
            if _sell_item_keywords and any(kw in last_bot_message for kw in _sell_item_keywords):
                kept = [kw for kw in _keep_item_keywords if kw in last_bot_message] if _keep_item_keywords else []
                if not kept:
                    _filter_sell_pending = True
        # 아이템 필터: 키워드 포함 시 강제 판매 (1~3강, 0강은 위에서 강화 처리)
        elif _sell_item_keywords and level is not None and 1 <= level <= 3 and any(kw in last_bot_message for kw in _sell_item_keywords):
            # keep 키워드가 있으면 판매 안 함
            kept = [kw for kw in _keep_item_keywords if kw in last_bot_message] if _keep_item_keywords else []
            if kept:
                matched = [kw for kw in _sell_item_keywords if kw in last_bot_message]
                print(f"✨ 아이템 보존 [{','.join(kept)}] - 판매 안 함 (lv.{level}, matched: {','.join(matched)})")
                # keep이면 일반 AI/heuristic으로 진행 (아래 else 블록으로)
                if fund is None:
                    fund = 0
                profit = fund - start_fund if start_fund else 0
                level_stats = " | ".join([f"{lv}강:{cnt}" for lv, cnt in sorted(level_counts.items())]) if level_counts else "없음"
                print(f"📊 골드: {fund:,}G ({profit:+,}) | 레벨: +{level} (최고:{max_level_achieved}) | 실패: {fail_count}회 | 달성: [{level_stats}]", end=" | ")
                if mode == 'ai':
                    inference_result = ai.predict(fund, level, fail_count)
                else:
                    inference_result = ai.heuristic(fund, level, fail_count)
                print(f"결정: {'강화' if inference_result == 0 else '판매' if inference_result == 1 else '대기'}")
            else:
                matched = [kw for kw in _sell_item_keywords if kw in last_bot_message]
                print(f"🚫 아이템 필터 감지 [{','.join(matched)}] - 강제 판매 (lv.{level})")
                inference_result = 1
                _filter_sell_pending = True  # 봇 응답 올 때까지 강화 차단
        # 골드 부족이면 무조건 판매 (목표 레벨 아닌 이상)
        elif is_out_of_gold and level is not None and level < MAX_LEVEL_FOR_ENHANCE:
            print("💸 골드 부족 감지 - 무조건 판매")
            inference_result = 1
        elif level is None:
            if force_enhance:
                inference_result = 0
                print("⚠️ 파싱 실패 - 강제 강화 시도")
            else:
                print("⚠️ 메시지 파싱 실패 (레벨 없음)")
                return
        else:
            # fund가 None이면 0으로 대체 (이전 값 사용 로직에서 처리 안 된 경우)
            if fund is None:
                fund = 0
            # 현재 상태 표시
            profit = fund - start_fund if start_fund else 0
            level_stats = " | ".join([f"{lv}강:{cnt}" for lv, cnt in sorted(level_counts.items())]) if level_counts else "없음"
            print(f"📊 골드: {fund:,}G ({profit:+,}) | 레벨: +{level} (최고:{max_level_achieved}) | 실패: {fail_count}회 | 달성: [{level_stats}]", end=" | ")

            if mode == 'ai':
                inference_result = ai.predict(fund, level, fail_count)
            else:
                inference_result = ai.heuristic(fund, level, fail_count)

            if inference_result == 2:
                print("결정: 🎉 목표 달성!")
            else:
                print(f"결정: {'강화' if inference_result == 0 else '판매' if inference_result == 1 else '대기'}")

    # Lock 밖에서 act_enhance/act_sell 호출 (각자 lock을 가짐)
    if inference_result == 0:
        act_enhance()
    elif inference_result == 1:
        act_sell()
    elif inference_result == 2:
        send_congratulation_message(level)
    else:
        print("⚠️ 행동 불가")

def on_press(key):
    global running_mode
    try:
        if key in pressed_keys:
            return
        pressed_keys.add(key)

        if key == keyboard.Key.f1:
            print("🔨 수동 강화")
            running_mode = None  # 자동 모드 중지
            act_enhance()
        elif key == keyboard.Key.f2:
            print("💵 수동 판매")
            running_mode = None  # 자동 모드 중지
            act_sell()
        elif key == keyboard.Key.f3:
            if running_mode == 'ai':
                print("⏸️ AI 모드 중지")
                running_mode = None
            else:
                print("🤖 AI 자동 모드 시작")
                running_mode = 'ai'
        elif key == keyboard.Key.f4:
            if running_mode == 'heuristic':
                print("⏸️ 규칙 기반 모드 중지")
                running_mode = None
            else:
                print("📋 규칙 기반 자동 모드 시작")
                running_mode = 'heuristic'
        elif key == keyboard.Key.f5:
            running_mode = None
            profit = (0 if start_fund is None else
                     (_parse_message(prev_text)[0] or start_fund) - start_fund)
            print("\n" + "="*60)
            print("👋 매크로 종료")
            print(f"📊 최종 통계:")
            print(f"   총 강화: {total_enhances}회 | 총 판매: {total_sells}회")
            print(f"   최고 레벨: {max_level_achieved}강")
            if level_counts:
                stats = " | ".join([f"{lv}강:{cnt}회" for lv, cnt in sorted(level_counts.items())])
                print(f"   레벨별 달성: {stats}")
            if start_fund:
                print(f"   순이익: {profit:+,}G")
            print("="*60)
            return False
        elif key == keyboard.Key.esc:
            print("\n⛔ 긴급 종료!")
            running_mode = None
            return False
    except AttributeError:
        pass

def on_release(key):
    try:
        pressed_keys.discard(key)
    except:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="검 강화 매크로")
    parser.add_argument("--mode", choices=["ai", "heuristic"], help="자동 시작 모드")
    parser.add_argument("--delay", type=int, default=10, help="자동 시작 대기 시간(초)")
    parser.add_argument("--profile", choices=list(COORD_PROFILES.keys()), default=DEFAULT_PROFILE, help="좌표 프로필")
    parser.add_argument("--until", type=str, default=None, help="종료 시각 (HH:MM, 예: 18:00)")
    parser.add_argument("--shutdown", action="store_true", help="종료 시 PC 강제 종료")
    parser.add_argument("--sell-items", type=str, default=None, help="강제 판매 키워드 (쉼표 구분, 예: 검,몽둥이)")
    parser.add_argument("--keep-items", type=str, default=None, help="판매 제외 키워드 (쉼표 구분, 예: 발렌타인)")
    args = parser.parse_args()

    # 아이템 필터 적용
    if args.sell_items:
        _sell_item_keywords = [kw.strip() for kw in args.sell_items.split(",") if kw.strip()]
    if args.keep_items:
        _keep_item_keywords = [kw.strip() for kw in args.keep_items.split(",") if kw.strip()]

    # 좌표 프로필 적용
    profile = COORD_PROFILES[args.profile]
    CHAT_OUTPUT_COORD_RATIO = profile["output"]
    CHAT_INPUT_COORD_RATIO = profile["input"]

    print("="*60)
    print("⚔️  검 강화 매크로 시작")
    print("="*60)
    print("조작키:")
    print("  F1: 수동 강화 | F2: 수동 판매")
    print("  F3: AI 자동 모드 | F4: 규칙 기반 자동 모드")
    print("  F5: 종료 | ESC: 긴급 종료")
    if _sell_item_keywords:
        print(f"  Item filter: [{', '.join(_sell_item_keywords)}] -> force sell")
    if _keep_item_keywords:
        print(f"  Item keep:   [{', '.join(_keep_item_keywords)}] -> never sell")
    print("="*60)
    print()

    if args.until:
        try:
            h, m = args.until.split(":")
            stop_time = datetime.now().replace(hour=int(h), minute=int(m), second=0)
            if stop_time <= datetime.now():
                stop_time += timedelta(days=1)
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            stop_str = stop_time.strftime("%Y-%m-%d %H:%M")
            print(f"  Now:  {now_str}")
            print(f"  Stop: {stop_str}" + (" + FORCE SHUTDOWN" if args.shutdown else ""))
        except ValueError:
            print(f"  [!] Invalid time format: {args.until} (use HH:MM)")
            args.until = None

    if args.until:
        def timer_check():
            global running_mode, is_running
            while is_running:
                now = datetime.now()
                if now >= stop_time:
                    running_mode = None
                    print(f"\n{'='*60}")
                    print(f"  >>> Timer: {args.until} - stopping macro")
                    if args.shutdown:
                        print(f"  >>> PC FORCE SHUTDOWN NOW")
                    print(f"{'='*60}")
                    if args.shutdown:
                        if platform.system() == 'Darwin':
                            subprocess.run(["sudo", "shutdown", "-h", "now"])
                        else:
                            subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
                    is_running = False
                    os._exit(0)
                time.sleep(10)
        threading.Thread(target=timer_check, daemon=True).start()

    if args.mode:
        mode_name = "AI" if args.mode == "ai" else "Heuristic"
        def auto_start():
            global running_mode
            for i in range(args.delay, 0, -1):
                print(f"  [{mode_name}] starting in {i}s...   ", end="\r")
                time.sleep(1)
            running_mode = args.mode
            print(f"\n{'='*60}")
            print(f"  >>> {mode_name} mode STARTED (profile: {args.profile})")
            print(f"{'='*60}")
        threading.Thread(target=auto_start, daemon=True).start()

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()