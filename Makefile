NAME := push_swap
CHECKER := checker

.PHONY: all clean fclean re test

all:
	@printf 'source layout pending\n'

clean:

fclean: clean
	@rm -f $(NAME) $(CHECKER)

re: fclean all

test:
	@printf 'tests pending\n'
