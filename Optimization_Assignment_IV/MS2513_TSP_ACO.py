# ------------------------------------------------------------
# Traveling Salesman Problem using Ant Colony Optimization (ACO)
# File: MS2513_TSP_ACO.py
# ------------------------------------------------------------

import random as rnd
import numpy as np
import math
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import time

# -----------------------
# City representation 
# -----------------------
class City:
    def __init__(self, lon, lat, cname, idx):
        self.lon = lon
        self.lat = lat
        self.cname = cname
        self.index = idx

    def distance(self, other):
        if self == other:
            return 0.0
        return math.hypot(self.lon - other.lon, self.lat - other.lat)

    def coords(self):
        return [self.lon, self.lat]

    def __repr__(self):
        return f"{self.cname}[{self.lon:.2f},{self.lat:.2f}]"

# -----------------------
# Read cities from file (Indian_cities.txt)
# -----------------------
def read_city_file(filename="Indian_cities.txt"):
    import os
    if not os.path.exists(filename) and os.path.exists("India_cities.txt"):
        filename = "India_cities.txt"
    cities = []
    geolocator = Nominatim(user_agent="KUNAL_TSP_ACO_2513")
    with open(filename, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            city_name = line.strip()
            if city_name == "":
                continue
            # attempt geocoding; handle occasional failures with retries
            loc = None
            attempts = 0
            while loc is None and attempts < 3:
                try:
                    loc = geolocator.geocode(city_name + ", India", timeout=10)
                except Exception as e:
                    attempts += 1
                    time.sleep(1)
                if loc is None and attempts < 3:
                    time.sleep(1)
            if loc is None:
                raise RuntimeError(f"Geocoding failed for city: {city_name}")
            lon, lat = round(loc.longitude, 2), round(loc.latitude, 2)
            print(f"City[{idx}] = {city_name} ({lon:.2f},{lat:.2f})")
            cities.append(City(lon, lat, city_name, idx))
    return cities

# -----------------------
# Utility functions
# -----------------------
def euclidean_distance_matrix(coords):
    n = len(coords)
    D = np.zeros((n, n))
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.hypot(xi - xj, yi - yj)
            D[i, j] = d
            D[j, i] = d
    return D

def tour_length(tour, D):
    total = 0.0
    for a, b in zip(tour, tour[1:] + [tour[0]]):
        total += D[a, b]
    return total

def plot_route_by_indices(indices, cities, title="Route (ACO)", pause=0.5):
    coords = [cities[i].coords() for i in indices] + [cities[indices[0]].coords()]
    coords = np.array(coords)
    plt.figure(figsize=(7, 6))
    plt.plot(coords[:, 0], coords[:, 1], "-o")
    for i in indices:
        city = cities[i]
        plt.annotate(city.cname, (city.lon, city.lat))
    plt.title(title)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.show(block=False)
    plt.pause(pause)
    plt.close()

# -----------------------
# Ant Colony Optimization class
# -----------------------
class AntColonyTSP:
    def __init__(
        self,
        D,
        n_ants=None,
        alpha=1.0,
        beta=2.0,
        rho=0.1,
        Q=1.0,
        init_pheromone=1.0,
        random_seed=None,
    ):
      
        if random_seed is not None:
            rnd.seed(random_seed)
            np.random.seed(random_seed)
        self.D = D
        self.n = D.shape[0]
        self.n_ants = n_ants or self.n
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q

        # initialize pheromone matrix
        self.tau = np.full((self.n, self.n), init_pheromone, dtype=float)
        epsilon = 1e-12
        self.eta = 1.0 / (D + epsilon)
        np.fill_diagonal(self.eta, 0.0)

        self.best_tour = None
        self.best_length = float("inf")

    def _select_next_city(self, current, visited_mask):
        allowed = ~visited_mask
        allowed[current] = False
        if not np.any(allowed):
            return None

        tau_vals = self.tau[current] ** self.alpha
        eta_vals = self.eta[current] ** self.beta
        numerators = tau_vals * eta_vals * allowed.astype(float)
        total = numerators.sum()
        if total <= 0:
            # if numerators are zero (unlikely), choose uniformly among allowed
            candidates = np.where(allowed)[0]
            return int(rnd.choice(candidates))
        probs = numerators / total
        # sample according to probs
        return int(np.random.choice(range(self.n), p=probs))

    def _construct_solution(self):
        start = rnd.randrange(self.n)
        tour = [start]
        visited_mask = np.zeros(self.n, dtype=bool)
        visited_mask[start] = True
        current = start
        while len(tour) < self.n:
            nxt = self._select_next_city(current, visited_mask)
            if nxt is None:
                break
            tour.append(nxt)
            visited_mask[nxt] = True
            current = nxt
        return tour

    def _update_pheromones(self, ants_tours):
        # evaporation
        self.tau *= (1.0 - self.rho)
        # deposit
        for tour, length in ants_tours:
            if length <= 0:
                continue
            delta = self.Q / length
            for a, b in zip(tour, tour[1:] + [tour[0]]):
                self.tau[a, b] += delta
                self.tau[b, a] += delta

    def run(self, n_iterations=100, verbose=False, plot_every=10, cities=None):
      
        for it in range(1, n_iterations + 1):
            ants_tours = []
            for _ in range(self.n_ants):
                tour = self._construct_solution()
                if len(tour) != self.n:
                    continue
                L = tour_length(tour, self.D)
                ants_tours.append((tour, L))
                if L < self.best_length:
                    self.best_length = L
                    self.best_tour = tour.copy()

            self._update_pheromones(ants_tours)

            if verbose and (it % max(1, n_iterations // 10) == 0 or it == 1):
                print(f"Iteration {it}/{n_iterations}, best_length={self.best_length:.4f}")

            # intermediate plotting with city names if requested
            if cities is not None and (plot_every > 0 and it % plot_every == 0):
                if self.best_tour is not None:
                    title = f"Iteration {it} - Best length: {self.best_length:.4f}"
                    plot_route_by_indices(self.best_tour, cities, title=title, pause=0.7)

        return self.best_tour, self.best_length

# -----------------------
# Main: ACO runner (mirrors structure of your GA main)
# -----------------------
def run_aco(cities, n_ants=20, alpha=1.0, beta=2.0, rho=0.1, Q=100.0, iterations=200, plot_every=20):
    coords = [c.coords() for c in cities]
    D = euclidean_distance_matrix(coords)

    colony = AntColonyTSP(
        D,
        n_ants=n_ants,
        alpha=alpha,
        beta=beta,
        rho=rho,
        Q=Q,
        init_pheromone=1.0,
        random_seed=42,
    )

    print("Running ACO...")
    best_tour, best_len = colony.run(n_iterations=iterations, verbose=True, plot_every=plot_every, cities=cities)
    print("ACO finished.")
    print("Best length found:", best_len)
    print("Best tour (city order):")
    for idx in best_tour:
        print(f"  {cities[idx].cname}")

    # final plot
    plot_route_by_indices(best_tour, cities, title=f"Final best route (length {best_len:.4f})", pause=2.0)

    return best_tour

# -----------------------
# If run as script
# -----------------------
if __name__ == "__main__":
    # Example usage
    city_data = read_city_file("Indian_cities.txt")
    print("\nNumber of Cities:", len(city_data))

    best = run_aco(
        cities=city_data,
        n_ants=max(10, len(city_data)),  # typical to use ~n ants
        alpha=1.0,
        beta=2.0,
        rho=0.1,
        Q=100.0,
        iterations=200,
        plot_every=20,  # show intermediate plot every 20 iterations
    )

    # The script already plots the final route before exiting.