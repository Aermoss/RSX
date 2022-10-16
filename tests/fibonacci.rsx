int fibonacci(int n) {
    if (n <= 1) return n;
    else return fibonacci(n - 1) + fibonacci(n - 2);
}

int fibonacci_alternative(int n) {
    int x = 0, y = 1, z;

    while (--n > 0) {
        z = x + y;
        x = y;
        y = z;
    }

    return z;
}