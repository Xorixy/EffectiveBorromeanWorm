#pragma once

struct simple_uint128 {
    unsigned long long int big { 0 };
    unsigned long long int small { 0 };
    void increment() {
        small++;
        if (small == 0) big++;
    }
    void add(unsigned long long int val) {
        unsigned long long int temp = small + val;
        if (small > temp) {
            big++;
        }
        small = temp;
    }

    void add(long long int val) {
        unsigned long long int temp = small + val;
        if (small > temp) {
            big++;
        }
        small = temp;
    }
};