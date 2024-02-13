// In the following C program, which pointers must alias with each other?
// Please output the response as a list of lists of pointers which must
// alias, in Python syntax.

int main(int argc, char **argv) {
  int number = 2;
  int *z = &number;
  *z = 3;
  return number;
}