#pragma once
#include <exception>
#include <string>

namespace sim {
    class SimulationException final : public std::exception
    {
        private:
        std::string m_error{}; // handle our own string

        public:
        explicit SimulationException(std::string_view error)
            : m_error{error}
        {
        }

        // std::exception::what() returns a const char*, so we must as well
        [[nodiscard]] const char* what() const noexcept override { return m_error.c_str(); }
    };
}