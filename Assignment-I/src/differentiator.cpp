// differentiator.cpp
// Implementation of the forward / backward / central difference formulas.

#include "../include/differentiator.h"
#include "../include/exceptions.h"
#include <cmath>

// Just checks that h makes sense before we go dividing by it.
// I put this in one place instead of copy-pasting the same "if" 3 times.
void Differentiator::validateStepSize(double h) {
    if (h <= 0.0 || std::isnan(h)) {
        throw InvalidStepSizeException(h);
    }
}

// forward difference: uses a point ahead of x
double Differentiator::forwardDifference(const MathFunction& func, double x, double h) {
    validateStepSize(h);
    return (func.evaluate(x + h) - func.evaluate(x)) / h;
}

// backward difference: uses a point behind x
double Differentiator::backwardDifference(const MathFunction& func, double x, double h) {
    validateStepSize(h);
    return (func.evaluate(x) - func.evaluate(x - h)) / h;
}

// central difference: uses one point ahead AND one point behind
// (this is usually the most accurate of the three, we'll see it
// confirmed in the results table / plot)
double Differentiator::centralDifference(const MathFunction& func, double x, double h) {
    validateStepSize(h);
    return (func.evaluate(x + h) - func.evaluate(x - h)) / (2.0 * h);
}
