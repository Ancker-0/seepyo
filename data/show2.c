#define N 100

void add(int *dest, int *a, int *b) {
  for (int i = 0; i < N; ++i)
    dest[i] = a[i] + b[i];
}

int main() {
  int a[N], b[N], c[N];
  for (int i = 0; i < N; ++i) {
    a[i] = i * i;
    b[i] = i + 2;
  }
  add(c, a, b);
  int ans = 0;
  for (int i = 0; i < N; ++i) {
    ans ^= c[i] * i;
  }
  return ans;
}
