// This is a C program. Please output the list of variable names that
// point to objects that can escape the function.

#include <stdlib.h>

struct point { int x; int y }

struct point *create_point(int x0, int y0) {
  struct point *result = (struct point *) malloc (sizeof (point));
  result->x = x0;
  result->y = y0;
  return result;
}