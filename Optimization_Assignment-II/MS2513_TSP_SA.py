from scipy import *
from numpy import *
from pylab import *
from geopy.geocoders import Nominatim
import random
import time


# Let's calculate the straight-line distance between two points (cities)
def Distance(P1, P2):
    # If both points are exactly the same, the distance is obviously zero!
    if P1 == P2:
        return 0.0

    # Using the good old Pythagorean theorem to find the distance
    d = sqrt((P1[0] - P2[0]) ** 2 + (P1[1] - P2[1]) ** 2)
    return d


# Find the total distance of our entire trip going through all cities in the given sequence
def TotalDistance(P, seq):
    dist = 0.0
    N = len(seq)

    # Loop through the cities one by one and add up the distances between them
    for i in range(N - 1):
        dist += Distance(P[seq[i]], P[seq[i + 1]])

    # Don't forget we have to return to our starting city to complete the tour!
    dist += Distance(P[seq[N - 1]], P[seq[0]])
    return dist


# This function reads the names of cities from a file and gets their coordinates on the map
def readCities(PNames):
    P = []

    # We use Nominatim to look up city coordinates. It needs an app name, so we give it one.
    geolocator = Nominatim(user_agent="OPT2_TSP_Assignment_Kunal")

    j = 0

    # Open our file with the city names
    with open("india_cities.txt") as file:

        for line in file:
            # Clean up the line by removing any trailing newlines
            city = line.rstrip("\n")

            # Stop reading if we hit an empty line
            if city == "":
                break

            # Add ", India" so the geocoder knows where to look
            theLocation = city + ", India"

            pt = None

            # Sometimes the geocoder fails, so we try up to 5 times for each city
            for attempt in range(5):
                try:
                    print("Finding location for:", city)

                    # Ask the geolocator for the coordinates, giving it up to 100 seconds to answer
                    pt = geolocator.geocode(
                        theLocation,
                        timeout=100
                    )

                    # If we found the coordinates, we can stop trying
                    if pt is not None:
                        break

                    print("Location not found for:", city)
                    break

                except Exception as e:
                    # Oops, something went wrong. Let's print the error.
                    print(
                        "Geocoding error for %s (attempt %d/5): %s"
                        % (city, attempt + 1, e)
                    )

                    # Wait a bit longer before trying again so we don't spam the server
                    time.sleep(5 * (attempt + 1))

            # If we STILL didn't get coordinates after all attempts, just skip this city
            if pt is None:
                print("Skipping city:", city)
                continue

            # Round off the latitude (y) and longitude (x) to 2 decimal places to keep it clean
            y = round(pt.latitude, 2)
            x = round(pt.longitude, 2)

            # Show the user what we found
            print(
                "City[%2d] = %s (%5.2f, %5.2f)"
                % (j, city, x, y)
            )

            # Store the coordinates and the city name in our lists
            P.insert(j, [x, y])
            PNames.insert(j, city)

            j += 1

            # Play nice with the server by waiting a tiny bit before the next request
            time.sleep(1.2)

    return P


# This function draws the cities and the path connecting them on a graph
def Plot(seq, P, dist, PNames):
    # Gather all the coordinates in the order of our current sequence
    Pt = [P[seq[i]] for i in range(len(seq))]
    # Add the starting city at the end to close the loop
    Pt += [P[seq[0]]]
    Pt = array(Pt)

    # Show the total distance right on top of the graph
    title("Total distance = " + str(dist))
    # Draw the lines and points
    plot(Pt[:, 0], Pt[:, 1], "-o")

    # Put the name of each city next to its point on the map
    for i in range(len(P)):
        annotate(
            PNames[i],
            (P[i][0], P[i][1])
        )

    # Finally, display the graph!
    show()


# This function tries to improve our route by swapping two cities in the sequence
def swap(P, seq, dist, N1, N2, temp, nCity):

    # Find the neighbors (Left and Right) of the first city in the sequence
    N1L = N1 - 1
    if N1L < 0:
        N1L += nCity  # Wrap around to the end if we go out of bounds

    N1R = N1 + 1
    if N1R >= nCity:
        N1R = 0       # Wrap around to the start

    # Find the neighbors (Left and Right) of the second city in the sequence
    N2L = N2 - 1
    if N2L < 0:
        N2L += nCity

    N2R = N2 + 1
    if N2R >= nCity:
        N2R = 0

    # Grab the actual city indexes for these spots
    I1 = seq[N1]
    I2 = seq[N2]
    I1L = seq[N1L]
    I1R = seq[N1R]
    I2L = seq[N2L]
    I2R = seq[N2R]

    # Calculate how much the distance changes if we make this swap
    delta = 0.0

    # Add the distance of the new connections
    delta += Distance(P[I1L], P[I2])
    delta += Distance(P[I1], P[I2R])

    # Subtract the distance of the old connections we are breaking
    delta -= Distance(P[I1L], P[I1])
    delta -= Distance(P[I2], P[I2R])

    # If the cities are NOT right next to each other, we have to adjust a bit more
    if (
        N1 != N2L
        and N1R != N2
        and N1R != N2L
        and N2 != N1L
    ):
        # Add new connections for the other side
        delta += Distance(P[I2], P[I1R])
        delta += Distance(P[I2L], P[I1])

        # Remove old connections from the other side
        delta -= Distance(P[I1], P[I1R])
        delta -= Distance(P[I2L], P[I2])

    # Decide if we should keep this swap. 
    # If delta is negative (shorter distance), prob will be > 1 so we always keep it.
    prob = 1.0

    # If the distance actually got longer (delta > 0), we might STILL keep it!
    # This prevents us from getting stuck in a local minimum.
    if delta > 0.0:
        prob = exp(-delta / temp)

    # Roll a random number between 0 and 1
    rndm = random.random()

    # If our random number is smaller than the probability, we keep the swap!
    if rndm < prob:
        # Update the total distance
        dist += delta

        # Actually swap the cities in the sequence
        seq[N1] = I2
        seq[N2] = I1

        # Double-check that our math was right (for debugging purposes)
        dif = abs(dist - TotalDistance(P, seq))
        if dif * dist > 0.01:
            print("in SWAP -->")
            print(
                "N1=%3d N2=%3d N1L=%3d N1R=%3d N2L=%3d N2R=%3d"
                % (N1, N2, N1L, N1R, N2L, N2R)
            )
            print(
                "I1=%3d I2=%3d I1L=%3d I1R=%3d I2L=%3d I2R=%3d"
                % (I1, I2, I1L, I1R, I2L, I2R)
            )
            print(
                "T=%f D=%f delta=%f p=%f rn=%f"
                % (temp, dist, delta, prob, rndm)
            )
            print(seq)
            input("Press Enter to continue...")

        return dist, True

    # If we decided not to keep the swap, return the old distance and say False
    return dist, False


# This function tries another trick: reversing a whole section of the route
def reverse(P, seq, dist, N1, N2, temp, nCity):

    # Get the neighbor to the left of our starting point
    N1L = N1 - 1
    if N1L < 0:
        N1L += nCity

    # Get the neighbor to the right of our ending point
    N2R = N2 + 1
    if N2R >= nCity:
        N2R = 0

    # Check to make sure we aren't trying to reverse the entire sequence or something weird
    if (N1 != N2R) and (N2 != N1L):
        # Calculate the change in total distance for this reversal
        delta = (
            Distance(P[seq[N1L]], P[seq[N2]])
            + Distance(P[seq[N1]], P[seq[N2R]])
            - Distance(P[seq[N1L]], P[seq[N1]])
            - Distance(P[seq[N2]], P[seq[N2R]])
        )
    else:
        # If the points don't make sense, just abort
        return dist, False

    # Like before, calculate our chance of accepting this change
    prob = 1.0

    # If the distance went up, we only accept it sometimes, based on the current 'temperature'
    if delta > 0:
        prob = exp(-delta / temp)

    # Roll the dice
    rndm = random.random()

    # Did we accept the change?
    if rndm < prob:
        # Update distance
        dist += delta

        i = N1
        j = N2

        # Actually flip the section of the sequence around!
        while i < j:
            seq[i], seq[j] = seq[j], seq[i]
            i += 1
            j -= 1

        # Debug check just to be sure we didn't break anything
        dif = abs(dist - TotalDistance(P, seq))
        if dif * dist > 0.01:
            print(
                "in REVERSE N1L=%3d N2R=%3d"
                % (N1L, N2R)
            )
            print(
                "N1=%3d N2=%3d T=%f D=%f delta=%f p=%f rn=%f"
                % (
                    N1,
                    N2,
                    temp,
                    dist,
                    delta,
                    prob,
                    rndm
                )
            )
            print(seq)
            input("Press Enter to continue...")

        return dist, True

    # We rejected the change
    return dist, False


# This is the main part of the program that runs when you start it
if __name__ == "__main__":

    PNames = []

    # Get all our cities and their coordinates
    P = readCities(PNames)
    nCity = len(P)

    # Make sure we got at least 2 cities, otherwise we can't make a trip!
    if nCity < 2:
        print("\nERROR: Not enough cities were found.")
        print("Please check your internet connection and city file.")
        exit()

    # Set up some rules for our Simulated Annealing "cooling" process
    maxTsteps = 250         # How many temperature steps to take
    fCool = 0.9             # How fast the temperature drops (90% each time)
    maxSwaps = 2000         # How many random moves to try at each temperature step
    maxAccepted = 10 * nCity

    # Start with a simple 0, 1, 2, 3... order for our cities
    seq = arange(0, nCity, 1)

    # Figure out how long this initial trip is
    dist = TotalDistance(P, seq)

    # Set our starting "temperature". A higher temp means more random bad moves are allowed at first.
    temp = 10.0 * dist

    print(seq)
    print(
        "\nnCity=%d dist=%f temp=%f\n"
        % (nCity, dist, temp)
    )

    input("Press Enter to continue...")

    # Show us the initial (probably messy!) route
    Plot(seq, P, dist, PNames)

    oldDist = 0.0
    convergenceCount = 0

    # Let the cooling process begin!
    for t in range(1, maxTsteps + 1):

        # If the temperature gets super low, the route has settled down and we can stop
        if temp < 1.0e-6:
            break

        accepted = 0
        iteration = 0

        # Try to mix things up a bunch of times at the current temperature
        while iteration <= maxSwaps:

            # Pick two random cities
            N1 = random.randint(0, nCity - 1)
            N2 = random.randint(0, nCity - 1)

            # Make sure they aren't the exact same city
            while N2 == N1:
                N2 = random.randint(0, nCity - 1)

            # Keep N1 as the smaller index just to keep things organized
            if N2 < N1:
                N1, N2 = N2, N1

            # Decide randomly whether to try a "swap" or a "reverse" maneuver
            chk = random.uniform(0, 1)

            # 50% chance to swap, but only if they aren't right next to each other
            if (
                chk < 0.5
                and (N1 + 1 != N2)
                and (N1 != ((N2 + 1) % nCity))
            ):
                dist, flag = swap(
                    P,
                    seq,
                    dist,
                    N1,
                    N2,
                    temp,
                    nCity
                )
            else:
                # The other 50% of the time, try reversing a section
                dist, flag = reverse(
                    P,
                    seq,
                    dist,
                    N1,
                    N2,
                    temp,
                    nCity
                )

            # Keep track of how many changes we actually kept
            if flag:
                accepted += 1

            iteration += 1

        # Show our progress after finishing one temperature step
        print("Iteration:", t)
        print("Temperature:", temp)
        print("Distance:", dist)
        print(seq)

        # Check if our distance has barely changed compared to last time
        if abs(dist - oldDist) < 1.0e-4:
            convergenceCount += 1
        else:
            convergenceCount = 0

        # If it hasn't changed for 4 steps in a row, we've probably found the best route!
        if convergenceCount >= 4:
            break

        # Every 25 steps, draw the map so we can watch it get better
        if t % 25 == 0:
            Plot(seq, P, dist, PNames)

        # Cool down the temperature for the next step (less bad moves will be allowed)
        temp *= fCool
        oldDist = dist

    # Show the final, optimized route!
    Plot(seq, P, dist, PNames)