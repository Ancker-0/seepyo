int g(int x) {
  return x * 2;
}

int f(int x) {
  return g(x) + 1;
}

int main() {
  return f(3);
}
