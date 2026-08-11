// functions.h
// This file declares the test functions we are going to differentiate.
// I used an abstract base class "MathFunction" so that every function
// knows two things about itself:
//   1) how to compute f(x)
//   2) what its EXACT derivative is (so we can compare against it later)
//
// Using inheritance here means main.cpp can just loop over a list of
// MathFunction pointers without caring which actual function it is.

#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <string>

// ---------- Abstract base class ----------
class MathFunction {
public:
    // pure virtual functions -> any class that inherits from this
    // MUST implement these, otherwise it won't compile
    virtual double evaluate(double x) const = 0;        // returns f(x)
    virtual double exactDerivative(double x) const = 0;  // returns f'(x), the true value
    virtual std::string getName() const = 0;             // just for printing nice output

    // virtual destructor is important here since we will delete
    // derived objects through a base class pointer
    virtual ~MathFunction() {}
};

// ---------- f(x) = e^x ----------
class ExponentialFunction : public MathFunction {
public:
    double evaluate(double x) const override;
    double exactDerivative(double x) const override;
    std::string getName() const override;
};

// ---------- f(x) = sin(x) ----------
class SineFunction : public MathFunction {
public:
    double evaluate(double x) const override;
    double exactDerivative(double x) const override;
    std::string getName() const override;
};

// ---------- f(x) = x^3 - 2x + 1 ----------
class PolynomialFunction : public MathFunction {
public:
    double evaluate(double x) const override;
    double exactDerivative(double x) const override;
    std::string getName() const override;
};

#endif // FUNCTIONS_H
