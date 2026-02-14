# File directiries and paths
LOG_DIR = "./logs/"
MODEL_DIR = "./models/"
MODEL_PATH = "./models/sword_ppo_final.zip"
STATS_PATH = "./models/vec_normalize.pkl"

# Macro config
LEVEL_THRESHOLD = 10
FAIL_COUNT_THRESHOLD = 50
MAX_LEVEL_FOR_ENHANCE = 19
FORCE_SELL_LEVEL = 999  # 이 레벨 이상이면 무조건 판매
DEBUG_MODE = False  # True로 설정하면 클릭 좌표를 출력

# 좌표 설정 방식: 비율(True) 또는 절대좌표(False)
# 원격 데스크톱 등 해상도가 변경되는 환경에서는 비율 모드 권장
USE_RELATIVE_COORDS = True

# 좌표 프로필 (--profile 인자로 선택)
# get_coordinates_pyautogui.py를 실행해서 비율을 확인하세요
COORD_PROFILES = {
    "home": {  # 집
        "output": (0.915, 0.180),
        "input": (0.908, 0.372),
    },
    "work": {  # 회사 (RDP)
        "output": (0.700, 0.511),
        "input": (0.697, 0.807),
    },
    "work_local": {  # 회사 PC 물리 모니터 (RDP 해제 후) - 재측정 필요!
        "output": (0.700, 0.511),
        "input": (0.697, 0.807),
    },
}
DEFAULT_PROFILE = "work"

# 기본 좌표 (DEFAULT_PROFILE에서 로드, --profile로 덮어쓰기 가능)
CHAT_OUTPUT_COORD_RATIO = COORD_PROFILES[DEFAULT_PROFILE]["output"]
CHAT_INPUT_COORD_RATIO = COORD_PROFILES[DEFAULT_PROFILE]["input"]

# 절대 좌표 (픽셀 단위, 하위 호환성용)
# USE_RELATIVE_COORDS=False 일 때만 사용됨
CHAT_OUTPUT_COORD = (4132, 1394)  # x, y coordinates of the chat output box
CHAT_INPUT_COORD = (4132, 1720)   # x, y coordinates of the chat input box

ACTION_DELAY = 0.1  # 자동 모드에서 다음 행동까지의 대기 시간 (초)

# Training config
TRAINING_TIMESTEPS = 1000000
N_ENVS = 8
N_STEPS = 2048
BATCH_SIZE = 64
LEARNING_RATE = 0.0003
GAMMA = 0.999

# Game Env config
MAX_STEPS = 1000
TARGET_RATE = 5
MINIMUM_FUND = 10000
MINIMUM_SELL_LEVEL = 5
REWARD_COEFF = 0.001