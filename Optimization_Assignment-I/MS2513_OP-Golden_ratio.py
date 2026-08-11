# Golden Ratio (Golden Section) Search Method
# Finding the minimum of f(x) = x^3 - 3x^2 + 7 in the interval [1, 3]

import math

# the function we want to minimize
def f(x):
    return x**3 - 3 * x**2 + 7


def main():
    # interval [a, b]
    a = 1.0
    b = 3.0

    # stopping tolerance, can be changed if more accuracy needed
    tol = 0.0001

    # golden ratio constant
    gr = (math.sqrt(5.0) - 1.0) / 2.0  # approx 0.618

    # two interior points
    x1 = b - gr * (b - a)
    x2 = a + gr * (b - a)

    f1 = f(x1)
    f2 = f(x2)

    iter_count = 0

    print("Golden Ratio Search Method")
    print("Function: f(x) = x^3 - 3x^2 + 7")
    print(f"Interval: [{a}, {b}]\n")

    print("Iter\t a\t\t b\t\t x1\t\t x2\t\t f(x1)\t\t f(x2)")

    # main loop, keep shrinking interval until it is small enough
    while (b - a) > tol:
        iter_count += 1

        print(f"{iter_count}\t{a:.6f}\t{b:.6f}\t{x1:.6f}\t{x2:.6f}\t{f1:.6f}\t{f2:.6f}")

        if f1 < f2:
            # minimum lies in [a, x2]
            b = x2
            x2 = x1
            f2 = f1
            x1 = b - gr * (b - a)
            f1 = f(x1)
        else:
            # minimum lies in [x1, b]
            a = x1
            x1 = x2
            f1 = f2
            x2 = a + gr * (b - a)
            f2 = f(x2)

    xmin = (a + b) / 2.0

    print(f"\nTotal iterations = {iter_count}")
    print(f"Approximate x for minimum = {xmin:.6f}")
    print(f"Minimum value f(x) = {f(xmin):.6f}")


if __name__ == "__main__":
    main()
