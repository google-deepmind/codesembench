// In the following C program, which pointers must alias with each other?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.
// This is test alias3.c

struct point { int x; int y };

void increment_points(struct point *p, int n) {
  int i = 0;
  struct point *p0 = p, *p1 = 0;
  while (i < n) {
    p0->x += 1;
    p0->y += 1;
    p1 = p[i];
    p0 = p0 + 1;
    i += 1;
  }
}