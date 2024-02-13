// In the following C program, which pointers must alias with each other
// after the execution of the line marked "HERE"?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

#include <stdio.h>

struct card {
  int suit;
  int rank;
};

void swap(struct card** x, struct card** y, struct card** z) {
  struct card *tmp = *z;
  *z = *y;
  *y = *x;
  *x = tmp;
}

// Inspired by three-card Monte
int main(int argc, char **argv) {
  struct card card0 = {1, 12};
  struct card card1 = {2, 2};
  struct card card2 = {3, 2};
  struct card *orig_c0 = &card0, *orig_c1 = &card1, *orig_c2 = &card2;
  struct card *c0 = &card0, *c1 = &card1, *c2 = &card2;
  swap(&c0, &c1, &c2);
  swap(&c0, &c1, &c2); // HERE
  printf("%d %d\n", c0->suit, c0->rank);
  printf("%d %d\n", orig_c1->suit, orig_c1->rank);
  printf("%d\n", c0 == orig_c1);
}
