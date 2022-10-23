int x() return 10;

int keywords_one() {
    int a = 0;

    {
        a += x();
    }

    return a;
}

int keywords_two() {
    int a = 0;

    do {
        a += x();
    }

    return a;
}

int keywords_three() {
    int a = 0;

    do {
        a += x();
    } while (a < 50);

    return a;
}

int keywords_four() {
    int a = 0;

    while (a <= 50) {
        a += x();
    }

    return a;
}

int keywords_five() {
    int a = 0;

    for (int i = 0; i < 10; i++) {
        if (i == 3) continue;
        if (i == 5) break;
        a += x() * i;
    }

    return a;
}

int keywords_six() {
    int a = 0;

    if (a == 0) a += 5;
    if (a == 5) a *= 2;

    if (a == 15) a = 20;
    else if (a == 10) a = 40;
    else a = 30;

    return a;
}

int keywords_seven() {
    int a = x();

    switch (a) {
        case 0: {
            return 1;
        }

        case 10: {
            return 8;
        }

        case 20: {
            return 4;
        }

        case 30: {
            return 2;
        }

        default: {
            return 0;
        }
    }
}