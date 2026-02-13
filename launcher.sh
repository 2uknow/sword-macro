#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PY="$(pwd)/.venv/bin/python3"
TB="$(pwd)/.venv/bin/tensorboard"

select_filter() {
    clear
    echo "=========================================="
    echo " Item filter"
    echo "=========================================="
    echo ""
    echo "  Sell items with specific keywords?"
    echo "  (items with keyword in name = force sell)"
    echo ""
    echo "  [1] No filter (default)"
    echo "  [2] Sell items containing: sword, club"
    echo "  [3] Custom keywords"
    echo "  [0] Back"
    echo ""
    SELL_ARGS=""
    read -rp "Select: " fchoice
    case "$fchoice" in
        2) SELL_ARGS="--sell-items 검,몽둥이" ;;
        3)
            read -rp "Keywords (comma-separated): " sell_kw
            if [[ -n "$sell_kw" ]]; then
                SELL_ARGS="--sell-items ${sell_kw}"
            fi
            ;;
        0) return 1 ;;
        *) ;;
    esac
    return 0
}

show_menu() {
    clear
    echo "=========================================="
    echo "       Sword Macro Launcher (macOS)"
    echo "=========================================="
    echo ""
    echo "  --- Macro ---"
    echo "  [1] Start macro (console)"
    echo "  [2] Start macro (background)"
    echo "  [3] Stop macro"
    echo ""
    echo "  --- Auto start (5s delay) ---"
    echo "  [a] Heuristic auto (F4) + profile select"
    echo "  [b] AI auto (F3) + profile select"
    echo ""
    echo "  --- Tools ---"
    echo "  [4] Get coordinates (pyautogui)"
    echo "  [5] Check screen info"
    echo "  [6] Test coordinates"
    echo "  [7] Train AI model"
    echo "  [8] TensorBoard"
    echo "  [9] Open config (editor)"
    echo ""
    echo "  [0] Exit"
    echo ""
    echo "=========================================="
}

select_profile() {
    local auto_mode="$1"
    local auto_label="$2"

    # Profile
    clear
    echo "=========================================="
    echo " ${auto_label} auto mode - Select profile"
    echo "=========================================="
    echo ""
    echo "  [1] Home"
    echo "  [2] Work (RDP)"
    echo "  [3] Work_local (physical monitor)"
    echo "  [0] Back"
    echo ""
    read -rp "Select: " pchoice
    local profile=""
    case "$pchoice" in
        1) profile="home" ;;
        2) profile="work" ;;
        3) profile="work_local" ;;
        0|*) return 1 ;;
    esac

    # Timer
    clear
    echo "=========================================="
    echo " ${auto_label} [${profile}] - Timer setting"
    echo "=========================================="
    echo ""
    echo "  Stop time? (HH:MM format, e.g. 18:00)"
    echo "  Press Enter to skip (run forever)"
    echo ""
    local stop_time=""
    read -rp "Stop at: " stop_time
    local timer_args=""
    if [[ -n "$stop_time" ]]; then
        timer_args="--until ${stop_time} --shutdown"
        echo ""
        echo "  >> Will stop at ${stop_time} + Mac shutdown"
    fi

    # Item filter
    SELL_ARGS=""
    if ! select_filter; then
        return 1
    fi

    # Run mode
    clear
    echo "=========================================="
    echo " ${auto_label} [${profile}] - Start"
    [[ -n "$SELL_ARGS" ]] && echo " Filter: $SELL_ARGS"
    [[ -n "$timer_args" ]] && echo " Timer: ${stop_time} + shutdown"
    echo "=========================================="
    echo ""
    echo "  [1] Console (foreground)"
    echo "  [2] Background"
    echo "  [0] Back"
    echo ""
    read -rp "Select: " rchoice
    case "$rchoice" in
        2)
            clear
            echo "=========================================="
            echo " ${auto_label} [${profile}] - background"
            echo "=========================================="
            echo ""
            # shellcheck disable=SC2086
            nohup "$PY" macro.py --mode "$auto_mode" --delay 5 \
                --profile "$profile" $timer_args $SELL_ARGS > /dev/null 2>&1 &
            echo "[OK] Macro started in background (5s delay). PID: $!"
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        0)
            return 1
            ;;
        *)
            clear
            echo "=========================================="
            echo " ${auto_label} [${profile}] - starting in 5s..."
            echo " Exit: F5 or ESC"
            echo "=========================================="
            echo ""
            # shellcheck disable=SC2086
            "$PY" macro.py --mode "$auto_mode" --delay 5 \
                --profile "$profile" $timer_args $SELL_ARGS
            echo ""
            read -rp "Press Enter to continue..."
            ;;
    esac
}

# Main loop
while true; do
    show_menu
    read -rp "Select: " choice
    case "$choice" in
        1)
            SELL_ARGS=""
            if select_filter; then
                clear
                echo "=========================================="
                echo " Macro start (console mode)"
                echo " Exit: F5 or ESC"
                [[ -n "$SELL_ARGS" ]] && echo " Filter: $SELL_ARGS"
                echo "=========================================="
                echo ""
                # shellcheck disable=SC2086
                "$PY" macro.py $SELL_ARGS
                echo ""
            fi
            read -rp "Press Enter to continue..."
            ;;
        2)
            SELL_ARGS=""
            if select_filter; then
                clear
                echo "=========================================="
                echo " Macro start (background)"
                [[ -n "$SELL_ARGS" ]] && echo " Filter: $SELL_ARGS"
                echo "=========================================="
                echo ""
                # shellcheck disable=SC2086
                nohup "$PY" macro.py $SELL_ARGS > /dev/null 2>&1 &
                echo "[OK] Macro started in background. PID: $!"
                echo "     Use menu [3] to stop."
                echo ""
            fi
            read -rp "Press Enter to continue..."
            ;;
        3)
            clear
            echo "=========================================="
            echo " Stop macro"
            echo "=========================================="
            echo ""
            if pkill -f "python.*macro\.py" 2>/dev/null; then
                echo "[OK] Macro stopped."
            else
                echo "[!] No background macro found."
            fi
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        4)
            clear
            echo "=========================================="
            echo " Get coordinates (pyautogui)"
            echo " Ctrl+C to exit"
            echo "=========================================="
            echo ""
            "$PY" get_coordinates_pyautogui.py
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        5)
            clear
            echo "=========================================="
            echo " Screen info"
            echo "=========================================="
            echo ""
            "$PY" check_screen_info.py
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        6)
            clear
            echo "=========================================="
            echo " Test coordinates"
            echo "=========================================="
            echo ""
            "$PY" test_coordinates.py
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        7)
            clear
            echo "=========================================="
            echo " Train AI model"
            echo "=========================================="
            echo ""
            echo "  [1] Default (1,000,000 steps)"
            echo "  [2] Long (5,000,000 steps)"
            echo "  [3] Extra long (10,000,000 steps)"
            echo "  [0] Back"
            echo ""
            read -rp "Select: " tchoice
            case "$tchoice" in
                1) "$PY" -m rl.train ;;
                2) "$PY" -m rl.train -t 5000000 ;;
                3) "$PY" -m rl.train -t 10000000 ;;
                *) continue ;;
            esac
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        8)
            clear
            echo "=========================================="
            echo " TensorBoard"
            echo " Open http://localhost:6006 in browser"
            echo " Ctrl+C to exit"
            echo "=========================================="
            echo ""
            open "http://localhost:6006"
            "$TB" --logdir ./logs/
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        9)
            clear
            echo "=========================================="
            echo " Open config"
            echo "=========================================="
            echo ""
            if command -v open &>/dev/null; then
                open -e rl/config.py
            else
                "${EDITOR:-nano}" rl/config.py
            fi
            echo "[OK] config.py opened in editor."
            echo ""
            read -rp "Press Enter to continue..."
            ;;
        a|A)
            select_profile "heuristic" "Heuristic" || true
            ;;
        b|B)
            select_profile "ai" "AI" || true
            ;;
        0)
            clear
            echo "Bye!"
            sleep 1
            exit 0
            ;;
        *)
            echo ""
            echo "[!] Invalid input."
            sleep 2
            ;;
    esac
done
