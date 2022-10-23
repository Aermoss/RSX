string arrays_one(int a, int b, ...) {
    return {"HELLO", "WORLD"}[a][b] + "#";
}

int arrays_two(int index) {
    int[] a = {0, 1, 2, 3, 4, 5};
    return a[index] * 100;
}

int[] x() return {6, 7, 8, 9, 10};

int arrays_three(int index) {
    return x()[index];
}

int arrays_four() {
    if ({1, 2, 3} == {1, 2, 3}) return true;
    else false;
}

int arrays_five() {
    if ({1, 2, 3} == {1, 2, 2}) return true;
    else false;
}

float[] arrays_six() {
    return {1.2f, 2.6f, 3.1f, 4.9f};
}

float arrays_seven(float[] array, int index) {
    return array[index];
}

int[] arrays_eight(int[] a, int[] b) {
    int[a.length() + b.length()] c;

    for (int i = 0; i < a.length(); i++) {
        c[i] = a[i];
    }

    for (int i = 0; i < b.length(); i++) {
        c[i + a.length()] = b[i];
    }

    return c;
}

int arrays_nine(int[] a) {
    return a.length();
}

int[] arrays_ten(int[] a) {
    int[a.length()] b;
    int index = 0;

    for (int i = a.length() - 1; i >= 0; i--) {
        b[index++] = a[i];
    }

    return b;
}