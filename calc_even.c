#include <stdint.h>

double calc_even(int64_t bottom, int64_t top) {
	bottom = bottom % 2 == 1 ? ++bottom : bottom;
	top = top % 2 == 1 ? --top : top;
	return top > bottom ? 0 : ((double)bottom + (double)top) / 2.0 * ((top - bottom)/2); 
}
