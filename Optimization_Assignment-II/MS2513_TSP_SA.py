"""
Traveling Salesman Problem solved using Simulated Annealing.
This script finds an optimal (shortest) path to visit a list of cities.
"""

import math
import random
import os
import numpy as np
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

def Distance(P1, P2):
    """
    Calculate the Euclidean distance between two points (cities).
    """
    if P1 == P2:
        return 0.0

    # Distance formula: sqrt((x1 - x2)^2 + (y1 - y2)^2)
    d = math.sqrt((P1[0] - P2[0])**2 + (P1[1] - P2[1])**2)
    return d

def TotalDistance(P, seq):
    """
    Calculate the total distance of a given sequence of cities (a complete tour).
    """
    dist = 0.0
    N = len(seq)
    
    # Add distances between consecutive cities
    for i in range(N - 1):
        dist += Distance(P[seq[i]], P[seq[i+1]])

    # Add distance from the last city back to the first city to complete the loop
    dist += Distance(P[seq[N-1]], P[seq[0]])

    return dist

def readCities(PNames):
    """
    Read city names from a text file and get their coordinates (latitude and longitude).
    """
    P = [] # List to store coordinates of cities

    # Setup the geolocator to fetch coordinates
    geolocator = Nominatim(user_agent="MyApp")

    j = 0
    with open("./india_cities.txt") as file:
        for line in file:
            city = line.rstrip('\n')
            if city == "":
                break

            theLocation = city + ", India"
            
            # Get the coordinates for the city
            pt = geolocator.geocode(theLocation, timeout=10000)
            y = round(pt.latitude, 2)
            x = round(pt.longitude, 2)
            
            print("City[%2d] = %s (%5.2f, %5.2f)" % (j, city, x, y))
            
            P.insert(j, [x, y])
            PNames.insert(j, city)
            j += 1

    return P

def Plot(seq, P, dist, PNames, filename=None):
    """
    Plot the cities and the path connecting them.
    Saves the plot as an image file if a filename is provided.
    """
    plt.clf() # Clear previous plot
    
    # Get the coordinates in the order of the sequence
    Pt = [P[seq[i]] for i in range(len(seq))]
    Pt += [P[seq[0]]] # Add the first city at the end to close the loop
    Pt = np.array(Pt)
    
    plt.title('Total distance = ' + str(dist))
    
    # Plot the path with markers at the cities
    plt.plot(Pt[:, 0], Pt[:, 1], '-o')

    # Add city names to the plot
    for i in range(len(P)):
        plt.annotate(PNames[i], (P[i][0], P[i][1]))
    
    if filename:
        plt.savefig(filename)
    else:
        plt.show()

def swap(P, seq, dist, N1, N2, temp, nCity):
    """
    Try to swap two cities in the path to see if it improves the total distance.
    """
    # Find neighbors of N1 in the sequence
    N1L = N1 - 1
    if N1L < 0:
        N1L += nCity
    N1R = N1 + 1
    if N1R >= nCity:
        N1R = 0

    # Find neighbors of N2 in the sequence
    N2L = N2 - 1
    if N2L < 0:
        N2L += nCity
    N2R = N2 + 1
    if N2R >= nCity:
        N2R = 0

    I1 = seq[N1]
    I2 = seq[N2]
    I1L = seq[N1L]
    I1R = seq[N1R]
    I2L = seq[N2L]
    I2R = seq[N2R]

    # Calculate the change in distance if we perform the swap
    delta = 0.0
    delta += Distance(P[I1L], P[I2])
    delta += Distance(P[I1], P[I2R])
    delta -= Distance(P[I1L], P[I1])
    delta -= Distance(P[I2], P[I2R])

    # Adjust for adjacent cities
    if N1 != N2L and N1R != N2 and N1R != N2L and N2 != N1L:
        delta += Distance(P[I2], P[I1R])
        delta += Distance(P[I2L], P[I1])
        delta -= Distance(P[I1], P[I1R])
        delta -= Distance(P[I2L], P[I2])

    # Acceptance probability for Simulated Annealing
    prob = 1.0
    if delta > 0.0:
        prob = math.exp(-delta / temp)

    rndm = random.random()

    # Accept the new path based on probability
    if rndm < prob:
        dist += delta
        seq[N1] = I2
        seq[N2] = I1
        return dist, True
    else:
        return dist, False

def reverse(P, seq, dist, N1, N2, temp, nCity):
    """
    Try to reverse a segment of the path to see if it improves the total distance.
    """
    N1L = N1 - 1
    if N1L < 0:
        N1L += nCity

    N2R = N2 + 1
    if N2R >= nCity:
        N2R = 0

    # Calculate the change in distance
    delta = 0.0
    if N1 != N2R and N2 != N1L:
        delta = (Distance(P[seq[N1L]], P[seq[N2]]) 
               + Distance(P[seq[N1]], P[seq[N2R]]) 
               - Distance(P[seq[N1L]], P[seq[N1]]) 
               - Distance(P[seq[N2]], P[seq[N2R]]))
    else:
        return dist, False

    # Acceptance probability for Simulated Annealing
    prob = 1.0
    if delta > 0.0:
        prob = math.exp(-delta / temp)

    rndm = random.random()

    # Accept the new path based on probability
    if rndm < prob:
        dist += delta

        # Reverse the sequence between N1 and N2
        i = N1
        j = N2
        while i < j:
            u = seq[i]
            seq[i] = seq[j]
            seq[j] = u
            i += 1
            j -= 1

        return dist, True
    else:
        return dist, False

if __name__ == '__main__':
    PNames = [] # List to store city names
    
    # Read the coordinates for all cities from our text file
    P = readCities(PNames)
    nCity = len(P)           # Total number of cities to visit

    # Configuration for Simulated Annealing
    maxTsteps = 250          # How many times we cool down the temperature
    fCool = 0.9              # The cooling rate (temperature multiplier)
    maxSwaps = 2000          # Maximum tries at each temperature step
    maxAccepted = 10 * nCity # Maximum accepted changes before cooling

    # Start with a simple sequence: 0, 1, 2, ...
    seq = np.arange(0, nCity, 1)

    # Calculate initial distance
    dist = TotalDistance(P, seq)

    # Starting temperature (should be high enough to allow many initial changes)
    temp = 10.0 * dist

    # Create folder for saving output graphs if it doesn't exist
    if not os.path.exists("graphs"):
        os.makedirs("graphs")

    print("\nInitial Sequence:")
    print(seq)
    print("\nNumber of Cities = %3d | Initial Distance = %f | Initial Temp = %f \n" % (nCity, dist, temp))

    # Plot and save the initial path
    Plot(seq, P, dist, PNames, filename="graphs/initial_path.png")

    oldDist = 0.0
    convergenceCount = 0

    # Start the Simulated Annealing process
    for t in range(1, maxTsteps + 1):
        if temp < 1.0e-6:
            break # Stop if it's too cold

        accepted = 0
        iteration = 0

        # Try making random swaps or reversals to find a better path
        while iteration <= maxSwaps:
            
            # Pick two random cities (N1 and N2) to modify the path
            N1 = -1
            while N1 < 0 or N1 >= nCity:
                # Get a random city index. Using standard integer conversion instead of C-style cast
                N1 = int(random.random() * 1000.0) % nCity

            N2 = -1
            while N2 < 0 or N2 >= nCity or N2 == N1:
                N2 = int(random.random() * 1000.0) % nCity

            # Ensure N1 is smaller than N2
            if N2 < N1:
                N1 = N1 + N2
                N2 = N1 - N2
                N1 = N1 - N2

            # Randomly decide whether to try swapping two cities or reversing a segment
            chk = random.uniform(0, 1)
            if chk < 0.5 and (N1 + 1 != N2) and (N1 != ((N2 + 1) % nCity)):
                dist, flag = swap(P, seq, dist, N1, N2, temp, nCity)
            else:
                dist, flag = reverse(P, seq, dist, N1, N2, temp, nCity)

            if flag:
                accepted += 1

            iteration += 1

        print("Iteration: %d temp=%f    dist=%f" % (t, temp, dist))
        print("seq = ")
        np.set_printoptions(precision=3)
        print(seq)
        print("%c%c" % ('\n', '\n'))
        
        # Check if the distance has stopped improving (convergence)
        if abs(dist - oldDist) < 1.0e-4:
            convergenceCount += 1
        else:
            convergenceCount = 0

        # Stop if we haven't improved after a few steps
        if convergenceCount >= 4:
            break

        # Save a plot of the current path every 25 steps to track progress
        if t % 25 == 0:
            Plot(seq, P, dist, PNames, filename=f"graphs/path_iter_{t}.png")

        # Lower the temperature (cool down)
        temp *= fCool
        oldDist = dist

    # Plot and save the final optimized path
    Plot(seq, P, dist, PNames, filename="graphs/final_path.png")
    print("\nOptimization Complete. All graphs saved in the 'graphs' folder.")
