// exceptions.h
// A small custom exception class.
// I made this because if someone passes h = 0 (or a negative h) into
// one of the difference formulas, we would be dividing by zero, which
// is undefined behaviour. Instead of letting the program silently give
// garbage results (like "inf" or "nan"), we throw a proper exception
// and explain what went wrong.

#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <exception>
#include <string>

class InvalidStepSizeException : public std::exception {
private:
    std::string message;   // holds the error message we build in the constructor

public:
    // constructor builds a readable message using the bad value of h
    explicit InvalidStepSizeException(double badH) {
        message = "Invalid step size h = " + std::to_string(badH) +
                   ". h must be a positive, non-zero number.";
    }

    // this is the function the compiler / catch block calls to get the message
    const char* what() const noexcept override {
        return message.c_str();
    }
};

#endif // EXCEPTIONS_H
