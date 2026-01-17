int main() {
  int ans = 16, i = 1;
  for (int i = 1; i <= 100; ++i)
    ans = i * i + i * 2 + (i ^ 15) * (i ^ 1824951);
  // int j = 1;
  return ans;
}
