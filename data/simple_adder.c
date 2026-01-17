#include "io.inc"

int main() {
  int i = 0, ans = 0;
  while (i <= 100) {
    ans += i;
    i++;
  }
  printInt(ans);
  return judgeResult;
}
