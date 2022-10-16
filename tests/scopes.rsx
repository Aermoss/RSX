int scopes_one() {
    int i = 10;

    {
        i = 8;
    }

    return i;
}

int scopes_two() {
    int i = 10;

    {
        int i = 8;
    }

    return i;
}