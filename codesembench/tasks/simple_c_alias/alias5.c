// In the following C program, which pointers must alias with each other
// after the execution of the line marked "HERE"?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

struct point { int x; int y };

void increment_points(struct point *p, int n) {
  int i = 0;
  struct point *p0 = p, *p1 = 0, *p2 = 0, *p3, *p4;
  while (i < n) {
    p0->x += 1;
    p0->y += 1;
    p1 = &p[i];
    p2 = &p[2*i];
    p0 = p0 + 1;
    i += 1;
    p3 = &p[i];
    p4 = &p[i-1];  // HERE
  }
}