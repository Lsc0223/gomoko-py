#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII字符五子棋人机对战程序
Terminal Gobang - Human vs AI Five-in-a-Row Game

功能特性：
- 15x15标准棋盘
- 人机对战模式
- 智能AI对手（基于评分系统）
- 悔棋功能
- 清晰的ASCII界面
"""

import os
import random
import time

# ==================== 常量定义 ====================
BOARD_SIZE = 15  # 棋盘尺寸
EMPTY = 0        # 空位
BLACK = 1        # 黑棋
WHITE = 2        # 白棋

# 棋子显示符号
SYMBOLS = {
    EMPTY: ' + ',
    BLACK: ' ● ',
    WHITE: ' ○ '
}

# ==================== 全局变量 ====================
board = []           # 棋盘数据
history = []         # 落子历史（用于悔棋）
game_over = False    # 游戏结束标志
current_player = BLACK  # 当前玩家
ai_enabled = True    # 是否启用AI
thinking = False     # AI思考状态标志

# ==================== 初始化函数 ====================
def init_board():
    """初始化棋盘"""
    global board, history, game_over, current_player
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    history = []
    game_over = False
    current_player = BLACK

def clear_screen():
    """清空屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== 棋盘渲染函数 ====================
def render_board():
    """渲染并显示棋盘"""
    clear_screen()
    
    print("\n" + "=" * 60)
    print("          ASCII字符五子棋 - 人机对战 v1.0")
    print("=" * 60)
    
    # 显示模式信息
    mode_str = "人机对战" if ai_enabled else "双人对战"
    print(f"  模式: {mode_str} | 当前回合: {'黑棋 ●' if current_player == BLACK else '白棋 ○'}")
    print("-" * 60)
    
    # 打印列坐标 (A-O)
    print("    ", end="")
    for i in range(BOARD_SIZE):
        col_letter = chr(ord('A') + i)
        print(f" {col_letter}  ", end="")
    print()
    
    # 打印棋盘主体
    print("  " + "─" * (BOARD_SIZE * 4 + 1))
    
    for row in range(BOARD_SIZE):
        # 行号
        row_num = str(row + 1).rjust(2)
        print(f"{row_num} │", end="")
        
        for col in range(BOARD_SIZE):
            print(f"{SYMBOLS[board[row][col]]}│", end="")
        print()
        
        # 分隔线
        print("  " + "─" * (BOARD_SIZE * 4 + 1))
    
    print("\n说明: 输入坐标落子(如 H8)，输入 undo 悔棋，restart 重新开始，quit 退出")

# ==================== 坐标处理函数 ====================
def parse_coordinate(input_str):
    """
    解析用户输入的坐标
    支持格式: H8, 8H, H 8, 8 H (不区分大小写)
    返回: (row, col) 从0开始索引，失败返回 None
    """
    input_str = input_str.strip().upper().replace(" ", "")
    
    if len(input_str) < 2:
        return None
    
    # 提取字母和数字
    letters = ""
    numbers = ""
    
    for char in input_str:
        if char.isalpha():
            letters += char
        elif char.isdigit():
            numbers += char
    
    if not letters or not numbers:
        return None
    
    try:
        col = ord(letters[0]) - ord('A')
        row = int(numbers) - 1
    except (ValueError, IndexError):
        return None
    
    # 验证坐标范围
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return (row, col)
    
    return None

def is_valid_move(row, col):
    """检查落子是否合法"""
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        return False
    return board[row][col] == EMPTY

# ==================== 落子函数 ====================
def make_move(row, col, player):
    """执行落子"""
    board[row][col] = player
    history.append((row, col, player))
    return check_win(row, col, player)

def undo_move():
    """悔棋一步"""
    if history:
        row, col, player = history.pop()
        board[row][col] = EMPTY
        return True
    return False

# ==================== 胜负判定函数 ====================
def check_win(row, col, player):
    """检查是否获胜"""
    directions = [
        (0, 1),   # 横向
        (1, 0),   # 纵向
        (1, 1),   # 右斜
        (1, -1)   # 左斜
    ]
    
    for dr, dc in directions:
        count = 1
        
        # 正方向检查
        r, c = row + dr, col + dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        
        # 反方向检查
        r, c = row - dr, col - dc
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        
        if count >= 5:
            return True
    
    return False

# ==================== AI系统 ====================
def evaluate_position(row, col, player):
    """
    评估某个位置的分数
    返回进攻分和防守分的元组
    """
    opponent = WHITE if player == BLACK else BLACK
    
    # 临时落子
    board[row][col] = player
    attack_score = evaluate_line(player)
    
    # 撤销落子
    board[row][col] = EMPTY
    
    # 评估防守（对手在此落子的威胁）
    board[row][col] = opponent
    defend_score = evaluate_line(opponent)
    board[row][col] = EMPTY
    
    return attack_score, defend_score

def evaluate_line(player):
    """评估某个方向上的棋子形态得分"""
    score = 0
    
    directions = [
        (0, 1),   # 横向
        (1, 0),   # 纵向
        (1, 1),   # 右斜
        (1, -1)   # 左斜
    ]
    
    for dr, dc in directions:
        line_score = 0
        
        # 统计各个方向上的连子数
        counts = count_consecutive(player, dr, dc)
        
        for count, open_ends in counts:
            if count >= 5:
                line_score += 100000  # 连五
            elif count == 4:
                if open_ends == 2:
                    line_score += 10000  # 活四
                else:
                    line_score += 1000   # 冲四
            elif count == 3:
                if open_ends == 2:
                    line_score += 1000   # 活三
                else:
                    line_score += 100    # 眠三
            elif count == 2:
                if open_ends == 2:
                    line_score += 100    # 活二
                else:
                    line_score += 10     # 眠二
        
        score += line_score
    
    return score

def count_consecutive(player, dr, dc):
    """
    统计某个方向上连续棋子的数量和两端空位情况
    返回: [(count, open_ends), ...] 的列表
    """
    results = []
    
    # 从每个位置开始检查
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # 只检查起点（避免重复计算）
            if not (0 <= row - dr < BOARD_SIZE and 0 <= col - dc < BOARD_SIZE):
                if board[row][col] == player:
                    # 向两个方向延伸
                    count = 1
                    
                    # 正方向
                    r, c = row + dr, col + dc
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
                        count += 1
                        r += dr
                        c += dc
                    
                    # 检查两端
                    open_ends = 0
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == EMPTY:
                        open_ends += 1
                    
                    r, c = row - dr, col - dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == EMPTY:
                        open_ends += 1
                    
                    if count >= 2:  # 只返回有意义的连子
                        results.append((count, open_ends))
    
    return results

def get_ai_move():
    """AI获取最佳落子位置"""
    best_score = -1
    best_moves = []
    
    # 获取所有已有棋子周围的有效位置
    candidates = get_candidate_positions()
    
    if not candidates:
        # 如果棋盘为空，下天元位置
        return (7, 7)
    
    for row, col in candidates:
        attack_score, defend_score = evaluate_position(row, col, WHITE)
        total_score = max(attack_score, defend_score)
        
        # 中心位置加分
        center_bonus = 0
        center_row, center_col = 7, 7
        dist_from_center = abs(row - center_row) + abs(col - center_col)
        center_bonus = max(0, 10 - dist_from_center) * 5
        
        total_score += center_bonus
        
        if total_score > best_score:
            best_score = total_score
            best_moves = [(row, col)]
        elif total_score == best_score:
            best_moves.append((row, col))
    
    # 随机选择最佳位置
    return random.choice(best_moves)

def get_candidate_positions():
    """获取候选位置（已有棋子周围1格范围内的空位）"""
    candidates = set()
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != EMPTY:
                # 检查周围8个方向
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0:
                            continue
                        
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                            candidates.add((nr, nc))
    
    return list(candidates)

# ==================== 游戏控制函数 ====================
def switch_player():
    """切换当前玩家"""
    global current_player
    current_player = WHITE if current_player == BLACK else BLACK

def print_message(msg):
    """打印消息"""
    print(f"\n  >> {msg}")

def game_loop():
    """主游戏循环"""
    global game_over
    
    init_board()
    
    while True:
        render_board()
        
        if game_over:
            winner = "黑棋 ●" if current_player == BLACK else "白棋 ○"
            print(f"\n  🎉 恭喜！{winner} 获胜！ 🎉")
            print("  输入 restart 重新开始，quit 退出")
        
        if ai_enabled and current_player == WHITE and not game_over:
            # AI回合
            print_message("AI 正在思考...")
            time.sleep(0.5)  # 增加一点思考时间，模拟真实感
            
            row, col = get_ai_move()
            if make_move(row, col, WHITE):
                game_over = True
            else:
                switch_player()
            
            continue
        
        # 获取用户输入
        try:
            user_input = input("\n  请输入坐标或指令: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  游戏已退出")
            break
        
        if not user_input:
            continue
        
        # 解析命令
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n  感谢游玩，再见！")
            break
        
        elif user_input.lower() in ['restart', 'r']:
            init_board()
            continue
        
        elif user_input.lower() in ['undo', 'u']:
            if history:
                # 人机模式回退两步
                if ai_enabled and len(history) >= 2:
                    undo_move()  # AI的落子
                    undo_move()  # 玩家的落子
                    switch_player()
                else:
                    undo_move()
                    switch_player()
                print_message("悔棋成功")
            else:
                print_message("没有可悔的棋")
            continue
        
        # 解析坐标
        coord = parse_coordinate(user_input)
        
        if coord is None:
            print_message("输入格式错误，请输入如 H8 或 8H 格式的坐标")
            continue
        
        row, col = coord
        
        if not is_valid_move(row, col):
            print_message("该位置已有棋子或超出范围")
            continue
        
        # 执行落子
        if make_move(row, col, current_player):
            game_over = True
        else:
            switch_player()

def show_menu():
    """显示主菜单"""
    clear_screen()
    print("\n" + "=" * 60)
    print("          ASCII字符五子棋 - 人机对战 v1.0")
    print("=" * 60)
    print("\n  选择游戏模式:")
    print("  1. 人机对战 (玩家执黑先行)")
    print("  2. 双人人对战")
    print("  3. 退出游戏")
    print("\n" + "-" * 60)
    
    while True:
        choice = input("\n  请输入选项 (1-3): ").strip()
        
        if choice == '1':
            global ai_enabled
            ai_enabled = True
            print_message("选择人机对战模式")
            return True
        elif choice == '2':
            ai_enabled = False
            print_message("选择双人对战模式")
            return True
        elif choice == '3':
            print("\n  感谢使用，再见！")
            return False
        else:
            print_message("无效选项，请输入 1、2 或 3")

def main():
    """主函数"""
    while show_menu():
        game_loop()
        
        # 游戏结束后询问
        while True:
            again = input("\n  是否继续游戏? (y/n): ").strip().lower()
            if again in ['y', 'yes', '是']:
                break
            elif again in ['n', 'no', '否']:
                print("\n  感谢游玩，再见！")
                return
            else:
                print_message("请输入 y 或 n")

if __name__ == "__main__":
    main()
