import json
import time

EPSILON = 1e-9   # 동점으로 볼 허용오차


def normalize_label(raw):
    """입력 라벨을 표준 라벨(Cross, X)로 바꾼다. 알 수 없으면 None."""
    text = str(raw).strip().lower()
    if text in ("+", "cross"):
        return "Cross"
    if text == "x":
        return "X"
    return None


def mac(pattern, filt):
    """2차원 패턴과 필터를 위치별로 곱해 모두 더한다. (반복문 직접 구현)"""
    n = len(pattern)
    total = 0.0
    for r in range(n):
        for c in range(n):
            total += pattern[r][c] * filt[r][c]
    return total


def decide(score_1, score_2):
    """두 점수를 비교해 1이 크면 'first', 2가 크면 'second', 동점이면 'tie'."""
    if abs(score_1 - score_2) < EPSILON:
        return "tie"
    return "first" if score_1 > score_2 else "second"

