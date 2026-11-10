import json

# ========== 도구 함수들 ==========
def mac(a, b):
    # a, b는 숫자들이 담긴 리스트 → 같은 위치끼리 곱해서 전부 더함
    total = 0
    for i in range(len(a)):
        total += a[i] * b[i]
    return total

def flatten(grid):
    # 2차원 그림을 1줄 리스트로 펴기
    flat = []
    for row in grid:
        for value in row:
            flat.append(value)
    return flat


# ========== 데이터 로드 (한 번만!) ==========
with open("data.json", "r") as f:
    data = json.load(f)


# ========== 판정 함수 ==========
def judge(pattern_key):
    # 1. 패턴 키로 데이터 꺼내기
    pattern = data["patterns"][pattern_key]
    input_grid = pattern["input"]
    answer = pattern["expected"]

    # 2. 크기 알아내기 (예: size_5_1 → size_5)
    parts = pattern_key.split("_")        # ['size', '5', '1']
    size_key = parts[0] + "_" + parts[1]  # 'size_5'

    # 3. 맞는 필터 꺼내기
    cross_filter = data["filters"][size_key]["cross"]
    x_filter     = data["filters"][size_key]["x"]

    # 4. 전부 1줄로 펴기
    flat_input = flatten(input_grid)
    flat_cross = flatten(cross_filter)
    flat_x     = flatten(x_filter)

    # 5. MAC으로 점수 계산
    cross_score = mac(flat_input, flat_cross)
    x_score     = mac(flat_input, flat_x)

    # 6. 동점/판정 (epsilon 허용오차)
    EPSILON = 1e-9
    if abs(cross_score - x_score) < EPSILON:
        prediction = "UNDECIDED"
    elif cross_score > x_score:
        prediction = "Cross"
    else:
        prediction = "X"

    # 7. 정답(answer) 정규화: '+' → Cross, 'x' → X
    if answer == "+":
        expected = "Cross"
    elif answer == "x":
        expected = "X"

    # 8. PASS / FAIL
    if prediction == expected:
        result = "PASS"
    else:
        result = "FAIL"

    # 9. 결과 출력
    print(f"[{pattern_key}] 판정: {prediction} | expected: {expected} | {result}")


# ========== 모든 패턴 반복 ==========
for key in data["patterns"]:
    judge(key)