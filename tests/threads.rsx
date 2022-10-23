include "rsxthread" : *;

int x = 0;

void a() {
    for (int i = 0; i < 10; i++) {
        x += 2;
    }
}

void b() {
    for (int i = 0; i < 10; i++) {
        x += 1;
    }
}

int threads_one() {
    int thread_a = std::thread("a", false);
    int thread_b = std::thread("b", false);
    std::start_thread(thread_a);
    std::start_thread(thread_b);
    return x;
}