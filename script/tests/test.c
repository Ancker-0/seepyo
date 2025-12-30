#include "io.inc"

void add(int n, int a[], int b[], int c[]) {
  int i;
  for (i = 0; i < n; i++)
    c[i] = a[i] + b[i];
}

int main() {
  const int N = 10;
  int a[N], b[N], c[N];
  int i;
  for (i = 0; i < N; i++) {
    a[i] = i * i;
    b[i] = 2 * i + 1;
  }
  add(N, a, b, c);
  for (i = 0; i < N; i++)
    printInt(c[i]);
  return judgeResult;
}
