#define N 100

int a[N];

int main() {
  for (int i = 0; i < 100; ++i)
    a[i] = i;
  int ans = 0;
  for (int i = 0; i < 100; ++i)
    ans += a[i];
  return ans;
}
