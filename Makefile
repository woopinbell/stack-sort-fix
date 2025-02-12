NAME := push_swap
CHECKER := checker
CC := cc
CFLAGS := -Wall -Wextra -Werror
CPPFLAGS := -Iinclude
RM := rm -f
RMDIR := rm -rf
OBJ_DIR := .build

COMMON_SRCS := \
	src/parser.c \
	src/stack.c \
	src/operations.c \
	src/utils.c
PUSH_SRCS := src/push_swap.c src/sort.c
CHECKER_SRCS := src/checker.c src/checker_reader.c

COMMON_OBJS := $(COMMON_SRCS:src/%.c=$(OBJ_DIR)/%.o)
PUSH_OBJS := $(PUSH_SRCS:src/%.c=$(OBJ_DIR)/%.o)
CHECKER_OBJS := $(CHECKER_SRCS:src/%.c=$(OBJ_DIR)/%.o)

.DELETE_ON_ERROR:
.PHONY: all clean fclean re test

all: $(NAME) $(CHECKER)

$(NAME): $(COMMON_OBJS) $(PUSH_OBJS)
	$(CC) $(CFLAGS) $(COMMON_OBJS) $(PUSH_OBJS) -o $@

$(CHECKER): $(COMMON_OBJS) $(CHECKER_OBJS)
	$(CC) $(CFLAGS) $(COMMON_OBJS) $(CHECKER_OBJS) -o $@

$(OBJ_DIR)/%.o: src/%.c include/push_swap.h | $(OBJ_DIR)
	$(CC) $(CFLAGS) $(CPPFLAGS) -c $< -o $@

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

clean:
	$(RMDIR) $(OBJ_DIR) tests/__pycache__ .pytest_cache

fclean: clean
	$(RM) $(NAME) $(CHECKER)

re: fclean all

test: all
	python3 tests/run_tests.py
