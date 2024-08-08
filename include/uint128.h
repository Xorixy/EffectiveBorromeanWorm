#pragma once
#include <vector>

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

struct simple_uint128_vec {
    std::vector<unsigned long long int> bigs;
    std::vector<unsigned long long int> smalls;

    void push_back(const simple_uint128 uint) {
        bigs.push_back(uint.big);
        smalls.push_back(uint.small);
    }

    simple_uint128_vec()
        : bigs(0)
        , smalls(0)
    {}

    explicit simple_uint128_vec(int n)
        : bigs(n)
        , smalls(n)
    {}

    void insert(const simple_uint128 uint, int n) {
        bigs.at(n) = uint.big;
        smalls.at(n) = uint.small;
    }
};