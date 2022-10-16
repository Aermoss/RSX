int factorial(int n) {
    if (n == 0) return 1;
    else return n * factorial(n - 1);
}

int factorial_alternative(int n) {
    int result = 1;

    while (n > 0) {
        result = result * n--;
    }

    return result;
}