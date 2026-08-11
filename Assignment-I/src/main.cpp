// main.cpp
// This is the driver program for Assignment II - "Which Numerical
// Differentiation Method Should We Trust?"
//
// What it does:
//   1) picks the 3 test functions (e^x, sin(x), x^3 - 2x + 1)
//   2) picks 6 step sizes h = 1e-1 ... 1e-6
//   3) for every function and every h, computes forward/backward/central
//      difference approximations of f'(1), compares to the exact value,
//      and works out the absolute error
//   4) prints a nice table to the screen
//   5) also saves everything into data/results.csv so I can make the
//      log-log error plot with it afterwards
//   6) demonstrates the exception handling by deliberately calling one
//      of the methods with an invalid h

#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <memory>   // for std::unique_ptr
#include <cmath>    // for std::fabs

#include "../include/functions.h"
#include "../include/differentiator.h"
#include "../include/exceptions.h"

int main() {

    // the point we are approximating f'(1) at, as asked in the assignment
    const double x0 = 1.0;

    // 6 step sizes, from big to small
    std::vector<double> hValues = {1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6};

    // list of test functions, stored as base class pointers (this is
    // the "OOP" part - main.cpp doesn't need to know the details of
    // each function, it just calls evaluate()/exactDerivative())
    std::vector<std::unique_ptr<MathFunction>> functions;
    functions.push_back(std::make_unique<ExponentialFunction>());
    functions.push_back(std::make_unique<SineFunction>());
    functions.push_back(std::make_unique<PolynomialFunction>());

    // open the csv file we will use later for plotting
    std::ofstream csvFile("data/results.csv");
    csvFile << "function,h,exact,forward,backward,central,"
            << "error_forward,error_backward,error_central\n";

    // just to make the console output line up nicely
    std::cout << std::scientific << std::setprecision(4);

    for (const auto& funcPtr : functions) {

        std::cout << "\n================================================\n";
        std::cout << "Function: " << funcPtr->getName() << "\n";
        std::cout << "================================================\n";
        std::cout << std::left
                  << std::setw(10) << "h"
                  << std::setw(16) << "Forward Err"
                  << std::setw(16) << "Backward Err"
                  << std::setw(16) << "Central Err" << "\n";

        double exact = funcPtr->exactDerivative(x0);

        for (double h : hValues) {
            // wrapping this in a try/catch even though we control the
            // h values ourselves - this is where the exception handling
            // would kick in if h was ever bad (see the demo at the
            // bottom of main() where we pass in an invalid h on purpose)
            try {
                double fwd = Differentiator::forwardDifference(*funcPtr, x0, h);
                double bwd = Differentiator::backwardDifference(*funcPtr, x0, h);
                double ctr = Differentiator::centralDifference(*funcPtr, x0, h);

                double errFwd = std::fabs(exact - fwd);
                double errBwd = std::fabs(exact - bwd);
                double errCtr = std::fabs(exact - ctr);

                std::cout << std::setw(14) << h
                          << std::setw(16) << errFwd
                          << std::setw(16) << errBwd
                          << std::setw(16) << errCtr << "\n";

                csvFile << funcPtr->getName() << "," << h << "," << exact << ","
                        << fwd << "," << bwd << "," << ctr << ","
                        << errFwd << "," << errBwd << "," << errCtr << "\n";

            } catch (const InvalidStepSizeException& ex) {
                // if validateStepSize() ever throws, we land here
                std::cerr << "Caught exception: " << ex.what() << "\n";
            }
        }
    }

    csvFile.close();
    std::cout << "\nResults also saved to data/results.csv\n";

    // ---------------------------------------------------------
    // quick demo that the exception handling actually works:
    // deliberately call central difference with h = 0
    // ---------------------------------------------------------
    std::cout << "\n--- exception handling demo (using h = 0 on purpose) ---\n";
    try {
        ExponentialFunction expFunc;
        double bad = Differentiator::centralDifference(expFunc, x0, 0.0);
        std::cout << "This line should never print: " << bad << "\n";
    } catch (const InvalidStepSizeException& ex) {
        std::cout << "Caught it! Message: " << ex.what() << "\n";
    }

    return 0;
}
