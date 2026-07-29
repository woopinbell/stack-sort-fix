# 개발 기록

배열 스택과 11개 연산을 먼저 만들고, 입력값을 상대 순위로 바꾼 뒤 작은 입력과
기수 정렬을 차례로 붙였다. `checker`는 그 다음에 같은 상태 전이를 출력 없이
재사용하도록 만들었고, 마지막에는 공통 구현만 믿지 않도록 독립 모델과 실패
주입을 더했다. 이 순서에서 생긴 표현, 알고리즘, 명령 스트림과 검증의 경계를
네 글로 나눴다.

1. [값과 순위의 표현 불변식](01-value-rank-invariant.md)
2. [작은 경우를 닫고 기수 정렬로 넓히기](02-small-input-and-radix-sort.md)
3. [제한된 명령 입력과 출력 실패](03-command-io-and-failures.md)
4. [독립 모델과 자원 회귀 검사](04-property-and-resource-tests.md)

전체 경로는 [생성부터 검증까지](../architecture/generator-and-checker.md),
알고리즘 선택은
[정렬 전략과 연산 비용](../architecture/sorting-and-operation-cost.md)에 정리했다.
