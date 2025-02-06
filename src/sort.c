#include "push_swap.h"

static int	find_rank_index(const t_stack *stack, int rank)
{
	int	i;

	i = 0;
	while (i < stack->size)
	{
		if (stack->ranks[i] == rank)
			return (i);
		i++;
	}
	return (-1);
}

static void	move_index_to_top(t_stack *a, int index)
{
	if (index <= a->size / 2)
	{
		while (index-- > 0)
			op_ra(a, 1);
	}
	else
	{
		index = a->size - index;
		while (index-- > 0)
			op_rra(a, 1);
	}
}

void	sort_stack(t_stack *a, t_stack *b)
{
	(void)b;
	if (a->size < 2 || stack_is_sorted(a))
		return ;
}
