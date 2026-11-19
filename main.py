"""README.md 에 보너스 과제 내용을 반영한다. (main.py 와 같은 폴더에서 실행)

사용법: python3 bonus_readme_patch.py
- 모드 선택 화면에 3번(보너스)을 추가하고, 8장을 '수행함'으로 바꾸고, 체크리스트를 보강한다.
- 8-2 의 측정 표는 이 컴퓨터에서 main.compare_performance() 를 실행해 그대로 넣는다.
"""
import contextlib
import io
from pathlib import Path

import main

readme_path = Path("README.md")
text = readme_path.read_text(encoding="utf-8")


def replace(old, new, count=1):
    global text
    found = text.count(old)
    if found != count:
        raise SystemExit(f"README 에서 찾을 문장이 {found}번 나옵니다(기대 {count}번): {old[:50]!r}")
    text = text.replace(old, new)


# 1) 모드 선택 화면 예시 3곳에 3번 추가
replace("2. data.json 분석\n선택",
        "2. data.json 분석\n3. 보너스 (패턴 생성기, 최적화 비교)\n선택", count=3)

# 2) 1장 개요 / 3장 실행 방법에 모드 3 설명 추가
replace("- **모드 2:** `data.json`의 필터(5×5, 13×13, 25×25)와 패턴을 일괄 판정하고, 성능 분석과 결과 요약을 출력한다.",
        "- **모드 2:** `data.json`의 필터(5×5, 13×13, 25×25)와 패턴을 일괄 판정하고, 성능 분석과 결과 요약을 출력한다.\n"
        "- **모드 3 (보너스):** N×N 십자가·X 패턴을 자동 생성해 판정하고, 2차원 배열 MAC과 1차원 배열 MAC의 시간을 비교한다.")
replace("- **모드 2:** 별도 입력 없이 `data.json`을 읽어 자동으로 분석한다. `data.json`은 `main.py`와 같은 폴더에 있어야 한다.",
        "- **모드 2:** 별도 입력 없이 `data.json`을 읽어 자동으로 분석한다. `data.json`은 `main.py`와 같은 폴더에 있어야 한다.\n"
        "- **모드 3 (보너스):** 보너스 메뉴에서 `1`(패턴 생성기, 3 이상의 홀수 N 입력) 또는 `2`(최적화 전/후 비교)를 고른다. `3`을 입력하면 종료한다.")

# 3) 8장 보너스 과제
bonus_old = "보너스 과제(1차원 배열 최적화, 패턴 생성기)는 수행하지 않았다."
if text.count(bonus_old) != 1:
    raise SystemExit("8장의 '수행하지 않았다' 문장을 찾지 못했습니다. 직접 8장을 확인하세요.")

buffer = io.StringIO()
with contextlib.redirect_stdout(buffer):
    main.compare_performance()
bench = buffer.getvalue().strip()

bonus_new = f"""보너스 과제 두 가지를 모드 3(보너스)으로 구현했다.

### 8-1. 패턴 생성기

크기 N을 입력하면 N×N 십자가(Cross)와 X 패턴을 자동으로 만든다. 만든 패턴은 기존 `mac()`과 `decide()`로 판정하고 `print_performance()`로 성능을 분석하는 데 그대로 재사용한다. 3×3 성능 측정용 기본 샘플(`CROSS_3X3`, `X_3X3`)도 이 생성기로 만든다.

| 패턴 | 규칙 | 함수 |
|---|---|---|
| Cross | 가운데 행(`r == N//2`) 또는 가운데 열(`c == N//2`)이 1 | `generate_cross(n)` |
| X | 두 대각선(`r == c` 또는 `r + c == N-1`)이 1 | `generate_x(n)` |

- **N은 3 이상의 홀수만 받는다.** 짝수는 가운데가 한 줄로 정해지지 않아 대칭 모양이 만들어지지 않기 때문이다. 숫자가 아니거나 짝수·3 미만이면 안내 후 다시 입력받는다.

```text
[생성된 Cross 5×5]
□ □ ■ □ □
□ □ ■ □ □
■ ■ ■ ■ ■
□ □ ■ □ □
□ □ ■ □ □

[생성된 X 5×5]
■ □ □ □ ■
□ ■ □ ■ □
□ □ ■ □ □
□ ■ □ ■ □
■ □ □ □ ■
#---------------------------------------
# 생성한 패턴 판정 (필터 A = Cross, 필터 B = X)
#---------------------------------------
입력 Cross| A 점수: 9.0 | B 점수: 1.0 | 판정: Cross | expected: Cross | PASS
입력 X    | A 점수: 1.0 | B 점수: 9.0 | 판정: X | expected: X | PASS
```

### 8-2. 시뮬레이터 최적화 (1차원 배열)

2차원 배열 `grid[r][c]`를 길이 N²의 1차원 배열로 펼치면(`flat[r*N + c]`) 이중 반복문이 반복문 하나로 줄어들어 접근 패턴이 단순해진다. 두 방식에 **같은 입력(Cross 필터, X 패턴)과 같은 반복 횟수({main.BONUS_REPEAT}회)**를 주고 평균 시간을 비교했다.

- **변환 비용:** `flatten()`은 준비 작업으로 한 번만 하면 되므로 측정에서 제외했다.
- **정확성:** 두 방식의 점수 차이가 epsilon(`1e-9`) 미만이면 `결과 일치`를 `OK`로 표시한다. 행을 차례로 이어 붙여 같은 순서로 곱하고 더하므로 점수는 같다.

```text
{bench}
```

- **해석:** `개선 배수`는 (2차원 시간) ÷ (1차원 시간)이다. 1보다 크면 1차원 방식이 빠른 것이다. 파이썬에서는 반복문 자체의 비용이 커서 이중 반복문을 하나로 줄여도 개선 폭이 크지 않을 수 있고, 크기가 커질수록 그 폭이 줄어들 수 있다. 값은 실행할 때마다, 컴퓨터마다 달라지므로 같은 조건의 전/후 비교로만 해석한다.
- **의미:** 실제 NPU에서는 데이터를 연속된 메모리에 한 줄로 놓아 읽는 것이 효율에 크게 영향을 준다. 이 실험은 그 아이디어를 파이썬 수준에서 확인해 본 것이다."""
replace(bonus_old, bonus_new)

# 4) 체크리스트 보강
replace("- [x] 결과 리포트에 실패 원인 분석과 시간 복잡도 O(N²) 근거 서술",
        "- [x] 결과 리포트에 실패 원인 분석과 시간 복잡도 O(N²) 근거 서술\n"
        "- [x] 보너스 1: 시뮬레이터 최적화(2차원 → 1차원 배열) 전/후 성능 비교\n"
        "- [x] 보너스 2: 패턴 생성기(N×N Cross/X)와 판정·성능 분석 재사용")

readme_path.write_text(text, encoding="utf-8")
print("README.md 에 보너스 과제를 반영했습니다.")
