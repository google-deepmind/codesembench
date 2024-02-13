// In the following C program, which pointers must alias with each other
// after the execution of the line marked "HERE"?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

struct x { int a; };

struct x *x0 = 0;
int i = 0;
int max = 50;

struct x **gen0 () {
  struct x **x0 = (struct x**)malloc(max * sizeof(struct x*));
  for (int i = 0; i < max; i++) {
    x0[i] = (struct x*)malloc(sizeof(struct x));
  }
  x0[0]->a = 1;
  x0[1]->a = 1;
  for (int i = 2; i < max; ++i) {
    x0[i]->a = x0[i-1]->a + x0[i-2]->a;
  }
  return x0;
} 

struct x** rep(struct x** orig) {
  struct x **result = gen0();
  if (orig != 0) {
    memcpy(result, orig, max*sizeof(struct x*));
  }
  return result;
}

int main(int argc, char ** argv) {
  struct x **x0 = rep(0);
  struct x **x1 = rep(x0);
  struct x **x2 = rep(x1);
  struct x **x3 = rep(0);
  for (int i = 0; i < max; i++) {
    if (x0[i]->a % 2 == 0) {
      x3[i] = x1[i];
    } else {
      x3[i] = x2[i];
    }
  }
  printf("%d\n", x3[0]->a);  // HERE
}
