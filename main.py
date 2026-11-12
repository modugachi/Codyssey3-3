import json
import math
import os
import time

EPSILON = 1e-9   # 동점으로 볼 허용오차

# data.json은 main.py가 있는 폴더에서 찾는다. (어느 폴더에서 실행해도 동작)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

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

# ========== 모드 2: data.json 분석 ==========
def load_data(path=DATA_FILE):
    """data.json을 읽어 dict로 돌려준다. 읽을 수 없으면 안내 후 None."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        print(f"⚠️ {path} 을(를) 읽을 수 없습니다: {error}")
        return None


def is_square(grid, n):
    """grid가 n×n 숫자 격자인지 확인한다."""
    if not isinstance(grid, list) or len(grid) != n:
        return False
    for row in grid:
        if not isinstance(row, list) or len(row) != n:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return False
    return True


def load_filters(data):
    """size_N 필터를 {N: {"Cross": 격자, "X": 격자}} 형태로 정리한다. (라벨 정규화 포함)"""
    filters = {}
    raw_filters = data.get("filters", {}) if isinstance(data, dict) else {}
    for size_key, pair in raw_filters.items():
        try:
            n = int(size_key.split("_")[1])            # 'size_5' -> 5
            standard = {}
            for raw_label, grid in pair.items():
                label = normalize_label(raw_label)     # 'cross' -> 'Cross'
                if label is None or not is_square(grid, n):
                    raise ValueError
                standard[label] = grid
            if set(standard) != {"Cross", "X"}:
                raise ValueError
            filters[n] = standard
            print(f"✓ {size_key} 필터 로드 완료 (Cross, X)")
        except (IndexError, ValueError, AttributeError):
            print(f"⚠️ {size_key} 필터 형식 오류: 이 필터는 건너뜁니다.")
    return filters


def run_case(key, case, filters):
    """케이스 1개를 처리해 결과 dict를 돌려준다. 어떤 오류가 있어도 프로그램이 죽지 않는다."""
    result = {"key": key, "cross": None, "x": None,
              "prediction": None, "expected": None,
              "status": "FAIL", "reason": ""}

    # 1) 키에서 크기 N 추출: size_5_1 -> 5
    try:
        n = int(key.split("_")[1])
    except (IndexError, ValueError, AttributeError):
        result["reason"] = "키에서 크기(N)를 읽을 수 없음"
        return result

    # 2) 해당 크기의 필터가 있는지
    if n not in filters:
        result["reason"] = f"size_{n} 필터가 없음"
        return result

    # 3) input / expected 항목이 있는지, expected 정규화
    try:
        grid = case["input"]
        raw_expected = case["expected"]
    except (KeyError, TypeError):
        result["reason"] = "input 또는 expected 항목이 없음 (스키마 오류)"
        return result
    expected = normalize_label(raw_expected)
    result["expected"] = expected
    if expected is None:
        result["reason"] = f"expected 라벨을 알 수 없음: {raw_expected!r}"
        return result

    # 4) 패턴 크기 검증 (필터와 같은 N×N인지)
    if not is_square(grid, n):
        result["reason"] = f"크기 불일치: 패턴이 {n}×{n} 숫자 격자가 아님"
        return result

    # 5) MAC 연산과 판정
    result["cross"] = mac(grid, filters[n]["Cross"])
    result["x"] = mac(grid, filters[n]["X"])
    outcome = decide(result["cross"], result["x"])
    result["prediction"] = {"first": "Cross", "second": "X", "tie": "UNDECIDED"}[outcome]

    # 6) PASS / FAIL
    if result["prediction"] == expected:
        result["status"] = "PASS"
    elif result["prediction"] == "UNDECIDED":
        result["reason"] = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
    else:
        result["reason"] = "판정과 expected 불일치"
    return result


def print_case(result):
    """케이스 결과 1개를 출력한다."""
    print(f"--- {result['key']} ---")
    if result["cross"] is not None:
        print(f"Cross 점수: {result['cross']}")
        print(f"X 점수: {result['x']}")
        print(f"판정: {result['prediction']} | expected: {result['expected']} | {result['status']}")
        if result["reason"]:
            print(f"  사유: {result['reason']}")
    else:
        print(f"판정 불가 | {result['status']}")
        print(f"  사유: {result['reason']}")


REPEAT = 10   # 성능 측정 반복 횟수

# 3×3 성능 측정용 기본 샘플 (십자가 필터, X 필터)
CROSS_3X3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
X_3X3 = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]


def measure(func, repeat=REPEAT):
    """func를 repeat번 실행해 평균 시간(ms)을 돌려준다. (연산 함수 호출 구간만 측정)"""
    total = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        func()
        total += time.perf_counter() - start
    return total / repeat * 1000


def print_performance(samples):
    """samples: [(N, 패턴, 필터), ...] 크기별 평균 시간과 연산 횟수 표를 출력한다."""
    print(f"{'크기':<10}{'평균 시간(ms)':<18}{'연산 횟수(N²)':<10}")
    print("-" * 38)
    for n, pattern, filt in samples:
        avg_ms = measure(lambda: mac(pattern, filt))
        print(f"{str(n) + '×' + str(n):<10}{avg_ms:<18.6f}{n * n:<10}")


def print_summary(results):
    """총 테스트 수, 통과 수, 실패 수와 실패 케이스 목록을 출력한다."""
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = [r for r in results if r["status"] == "FAIL"]
    print(f"총 테스트: {len(results)}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failed)}개")
    if failed:
        print("실패 케이스:")
        for r in failed:
            print(f"- {r['key']}: {r['reason']}")


def run_data_mode():
    """data.json 모드: 필터 로드 → 패턴 분석 → 성능 분석 → 결과 요약."""
    data = load_data()
    if data is None:
        return []

    print("#" + "-" * 39)
    print("# [1] 필터 로드")
    print("#" + "-" * 39)
    filters = load_filters(data)

    print("#" + "-" * 39)
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#" + "-" * 39)
    patterns = data.get("patterns") if isinstance(data, dict) else None
    if not isinstance(patterns, dict):
        print("⚠️ patterns 항목이 없거나 형식이 올바르지 않습니다.")
        return []

    results = []
    for key, case in patterns.items():
        result = run_case(key, case, filters)
        print_case(result)
        results.append(result)

    print("#" + "-" * 39)
    print(f"# [3] 성능 분석 (평균/{REPEAT}회)")
    print("#" + "-" * 39)
    samples = [(3, CROSS_3X3, X_3X3)]
    for n in sorted(filters):
        samples.append((n, filters[n]["Cross"], filters[n]["X"]))
    print_performance(samples)

    print("#" + "-" * 39)
    print("# [4] 결과 요약")
    print("#" + "-" * 39)
    print_summary(results)
    return results


# ========== 모드 1: 사용자 입력 (3×3) ==========
def parse_row(text, n):
    """공백으로 구분된 n개의 숫자 한 줄을 리스트로 바꾼다. 형식이 틀리면 None."""
    parts = text.split()
    if len(parts) != n:                      # 열 개수 불일치
        return None
    row = []
    for part in parts:
        try:
            value = float(part)              # 숫자 파싱 실패 (예: abc)
        except ValueError:
            return None
        if not math.isfinite(value):         # nan, inf 제외
            return None
        row.append(value)
    return row


def read_grid(title, n=3):
    """n줄을 입력받아 n×n 격자를 돌려준다. 잘못 입력한 줄은 그 줄만 다시 입력받는다."""
    print(f"{title} ({n}줄 입력, 공백 구분)")
    grid = []
    while len(grid) < n:
        row = parse_row(input(), n)
        if row is None:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
            continue
        grid.append(row)
    return grid


def print_grid(grid):
    """격자를 한 줄씩 출력한다."""
    for row in grid:
        print("  " + " ".join(str(value) for value in row))


def run_user_mode():
    """사용자 입력 모드: 필터 A, B 입력 → 저장 확인 → 패턴 입력 → MAC → 판정 → 성능 분석."""
    print("#" + "-" * 39)
    print("# [1] 필터 입력")
    print("#" + "-" * 39)
    filter_a = read_grid("필터 A")
    filter_b = read_grid("필터 B")
    print("✓ 필터 A, B 저장 완료")
    print("필터 A:")
    print_grid(filter_a)
    print("필터 B:")
    print_grid(filter_b)

    print("#" + "-" * 39)
    print("# [2] 패턴 입력")
    print("#" + "-" * 39)
    pattern = read_grid("패턴")

    print("#" + "-" * 39)
    print("# [3] MAC 결과")
    print("#" + "-" * 39)
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = measure(lambda: (mac(pattern, filter_a), mac(pattern, filter_b)))
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{REPEAT}회): {avg_ms:.6f} ms")
    outcome = decide(score_a, score_b)
    if outcome == "tie":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {'A' if outcome == 'first' else 'B'}")

    print("#" + "-" * 39)
    print(f"# [4] 성능 분석 (3×3, 평균/{REPEAT}회)")
    print("#" + "-" * 39)
    print_performance([(3, pattern, filter_a)])


# ========== 메뉴 ==========
def main():
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    try:
        while True:
            choice = input("선택: ").strip()
            if choice == "1":
                run_user_mode()
                break
            if choice == "2":
                run_data_mode()
                break
            print("⚠️ 잘못된 입력입니다. 1 또는 2를 입력하세요.")
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()