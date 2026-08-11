// functions.cpp
// Implementation of the test function classes declared in functions.h

#include "../include/functions.h"
#include <cmath>   // need this for exp(), sin(), cos()

// ---------------- ExponentialFunction ----------------
// f(x) = e^x , f'(x) = e^x (its own derivative, nice and simple)
double ExponentialFunction::evaluate(double x) const {
    return std::exp(x);
}

double ExponentialFunction::exactDerivative(double x) const {
    return std::exp(x);
}

std::string ExponentialFunction::getName() const {
    return "f(x) = e^x";
}

// ---------------- SineFunction ----------------
// f(x) = sin(x) , f'(x) = cos(x)
double SineFunction::evaluate(double x) const {
    return std::sin(x);
}

double SineFunction::exactDerivative(double x) const {
    return std::cos(x);
}

std::string SineFunction::getName() const {
    return "f(x) = sin(x)";
}

// ---------------- PolynomialFunction ----------------
// f(x) = x^3 - 2x + 1 , f'(x) = 3x^2 - 2
double PolynomialFunction::evaluate(double x) const {
    return (x * x * x) - (2.0 * x) + 1.0;
}

double PolynomialFunction::exactDerivative(double x) const {
    return (3.0 * x * x) - 2.0;
}

std::string PolynomialFunction::getName() const {
    return "f(x) = x^3 - 2x + 1";
}
