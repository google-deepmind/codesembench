// In the following C program, which pointers must alias with each other?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

int fn (int x, int y, int *p) {
  int *m0 = p;
  int *m1 = p + 1;
  if (x > y) {
    *m0 = x;
    *m1 = y;
  } else {
    *m0 = y;
    *m1 = x;
  }
  return 0
}
