# 제한된 명령 입력과 출력 실패

## 명령 길이는 읽는 동안 제한한다

checker가 무제한 줄을 먼저 할당한 뒤 명령을 검사하면 공격적인 stdin이 메모리를
계속 늘릴 수 있다. 가장 긴 유효 명령은 `rrr`의 3바이트이므로
`src/checker_reader.c`는 처음부터 4바이트만 할당한다.

```c
*line = (char *)ps_malloc(PS_COMMAND_MAX + 1);
...
if (c == '\0' || len >= PS_COMMAND_MAX)
	return (ps_free(*line), *line = NULL, -1);
```

EOF 앞에 개행이 없는 마지막 명령은 허용한다. EOF에서 길이가 0이면 정상 입력
종료이고, 빈 줄은 길이 0인 명령으로 parser가 거절한다.
`tests/fault_tests.py`는 NUL 포함, `rrrr`의 개행 유무, 빈 줄과 65,536바이트
입력을 모두 `Error`로 끝내는지 확인한다.

## `EINTR`만 자동 재시도한다

읽기와 쓰기가 시그널로 중단되면 같은 구간을 다시 시도한다. 쓰기가 양수 일부만 성공하면 성공한 길이만큼 전진한다. 0바이트 쓰기와 다른 오류는 진행 불가능한 실패다.

blocking stdin을 전제로 하므로 `EAGAIN`은 대기하지 않는다. event loop가 있는 애플리케이션이라면 “아직 준비되지 않음”을 별도 상태로 반환해야 한다.

## 명령 출력 실패는 정렬 실패다

`push_swap`의 연산은 상태를 바꾼 뒤 명령을 출력한다.

```c
static int	emit_op(const char *name, int emit)
{
	if (emit)
	{
		if (!ps_putstr_fd(1, name))
			return (0);
		ps_record_operation();
	}
	return (1);
}
```

출력 실패 뒤 메모리 상태를 되돌리지 않는다. 소비자가 완전한 명령열을 받지
못했으므로 즉시 실패를 전파하고 프로세스가 `Error`로 끝나는 것이 계약이다.
부분 출력은 이미 외부로 나가 되돌릴 수 없다.

fault 빌드는 `PS_FAIL_*_AT`, `PS_EINTR_*_AT`,
`PS_SHORT_WRITE_AT`, `PS_ZERO_WRITE_AT`으로 N번째 호출을 바꾼다.
`tests/fault_tests.py`는 모든 명령 출력 위치의 실패, 짧은 쓰기 뒤 영구 오류,
읽기·쓰기 `EINTR`와 0바이트 쓰기를 확인한다. `PS_LIVE_ALLOCATIONS=0` 보고가
없거나 제한 시간 3초를 넘겨도 실패다.

두 실행 파일은 시작할 때 `SIGPIPE`를 무시해 닫힌 stdout에서 신호로 갑자기
종료하지 않고 `EPIPE`를 일반 오류로 처리한다. 이는 프로세스 전체 신호 정책을
바꾸는 선택이며, 라이브러리로 재사용한다면 호출자 정책과 충돌할 수 있다.

```sh
make test
```
