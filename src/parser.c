#include "push_swap.h"

static int	is_space(char c)
{
	return (c == ' ' || c == '\t' || c == '\n'
		|| c == '\r' || c == '\v' || c == '\f');
}

static int	count_tokens_in_arg(const char *arg)
{
	int	count;
	int	i;

	count = 0;
	i = 0;
	while (arg[i] != '\0')
	{
		while (is_space(arg[i]))
			i++;
		if (arg[i] == '\0')
			break ;
		count++;
		while (arg[i] != '\0' && !is_space(arg[i]))
			i++;
	}
	return (count);
}

static int	count_all_tokens(int argc, char **argv)
{
	int	count;
	int	i;

	count = 0;
	i = 1;
	while (i < argc)
	{
		count += count_tokens_in_arg(argv[i]);
		i++;
	}
	return (count);
}

int	parse_input(int argc, char **argv, t_stack *a)
{
	int	count;

	stack_init_empty(a);
	if (argc == 1)
		return (1);
	count = count_all_tokens(argc, argv);
	if (count == 0)
		return (0);
	if (!stack_init(a, count))
		return (0);
	a->size = count;
	return (1);
}
