int main() {
  int ans;
  for (int i = 0; i < 50; ++i)
    if (30 < i + i && i + i - 1 < 50)
      for (int j = 0; j < 10; ++j)
        if (i * j < 200)
          ans += i * j * j;
  return ans;
}
