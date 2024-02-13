// In the following C program, which pointers must alias with each other
// after the execution of the line marked "HERE"?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

#include <stdlib.h>
#include <stdio.h>

struct x { int a; };

struct x *x0 = 0;
int i = 0;

struct x *gen0 () {
  if (x0 == 0) {
    x0 = (struct x*)malloc(3 * sizeof(struct x));
  }
  struct x* result = x0 + i;
  i = (i + 1) % 3;
  return result;
} 

struct x *rep0() {
  return gen0();
}

int main(int argc, char ** argv) {
  struct x *x0 = rep0();
  struct x *x1 = rep0();
  struct x *x2 = rep0();
  struct x *x3 = rep0();
  x0->a = 1;
  x1->a = 2;
  x2->a = 3;
  x3->a = 4; // HERE
  printf("%d", x0->a);
}