This is a C program. Can the struct that is pointed to by result escape
the function?
    
#include <stdlib.h>

struct point { int x; int y }

struct point *create_point(int x0, int y0) {
  struct point *result = (struct point *) malloc (sizeof (point));
  result->x = x0;
  result->y = y0;
  return result;
}