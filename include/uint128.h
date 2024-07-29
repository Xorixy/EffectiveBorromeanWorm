#pragma once

struct simple_uint128 {
    unsigned long long int big { 0 };
    unsigned long long int small { 0 };
    uint128& operator++() {
        small++;
        if (small == 0) big++;
    }
};