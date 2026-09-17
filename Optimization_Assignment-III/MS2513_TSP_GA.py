# ------------------------------------------------------------
# Traveling Salesman Problem using Genetic Algorithm
# File: MS2513_TSP_GA.py
# ------------------------------------------------------------

import random as rnd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim


# ------------------------------------------------------------
# Class for city representation
# ------------------------------------------------------------
class City:
    def __init__(self, lon, lat, cname, idx):
        self.lon = lon
        self.lat = lat
        self.cname = cname
        self.index = idx

    def distance(self, other):
        if self == other:
            return 0.0
        return np.sqrt((self.lon - other.lon) ** 2 + (self.lat - other.lat) ** 2)

    def coords(self):
        return [self.lon, self.lat]

    def __repr__(self):
        return f"{self.cname}[{self.lon:.2f},{self.lat:.2f}]"


# ------------------------------------------------------------
# Fitness class for a route
# ------------------------------------------------------------
class RouteFitness:
    def __init__(self, route):
        self.route = route
        self.total_distance = 0.0
        self.fitness_value = 0.0

    def length(self):
        dist = 0.0
        for i in range(len(self.route)):
            from_city = self.route[i]
            to_city = self.route[(i + 1) % len(self.route)]
            dist += from_city.distance(to_city)
        self.total_distance = dist
        return dist

    def fitness(self):
        if self.total_distance == 0.0:
            self.length()
        self.fitness_value = 1.0 / self.total_distance
        return self.fitness_value


# ------------------------------------------------------------
# Read cities from file (India_cities_GA.txt)
# ------------------------------------------------------------
def read_city_file():
    cities = []
    geolocator = Nominatim(user_agent="TSP_Kunal_MS2513")

    with open("India_cities_GA.txt") as f:
        for idx, line in enumerate(f):
            city = line.strip()
            if city == "":
                break
            loc = geolocator.geocode(city + ", India", timeout=10)
            lon, lat = round(loc.longitude, 2), round(loc.latitude, 2)
            print(f"City[{idx}] = {city} ({lon:.2f},{lat:.2f})")
            cities.append(City(lon, lat, city, idx))
    return cities


# ------------------------------------------------------------
# GA helper functions
# ------------------------------------------------------------
def create_route(city_list):
    return rnd.sample(city_list, len(city_list))


def init_population(pop_size, city_list):
    return [create_route(city_list) for _ in range(pop_size)]


def rank_routes(population):
    scores = {i: RouteFitness(population[i]).fitness() for i in range(len(population))}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def select_mating_pool(ranked, elite_size):
    selection = []
    # keep elite
    for i in range(elite_size):
        selection.append(ranked[i][0])

    df = pd.DataFrame(np.array(ranked), columns=["Index", "Fitness"])
    df["cum_sum"] = df.Fitness.cumsum()
    df["cum_perc"] = 100 * df.cum_sum / df.Fitness.sum()

    # roulette wheel
    for _ in range(len(ranked) - elite_size):
        pick = 100 * rnd.random()
        for i in range(len(ranked)):
            if pick <= df.iat[i, 3]:
                selection.append(ranked[i][0])
                break
    return selection


def mating_pool(population, selected_idx):
    return [population[i] for i in selected_idx]


def crossover(parent1, parent2):
    child = []
    gene_a, gene_b = sorted([int(rnd.random() * len(parent1)), int(rnd.random() * len(parent1))])
    child_part = parent1[gene_a:gene_b]
    child_rest = [c for c in parent2 if c not in child_part]
    child = child_part + child_rest
    return child


def breed_population(pool, elite_size):
    children = pool[:elite_size]
    shuffled = rnd.sample(pool, len(pool))
    for i in range(len(pool) - elite_size):
        children.append(crossover(shuffled[i], shuffled[-i - 1]))
    return children


def mutate(route, mutation_rate):
    for swapped in range(len(route)):
        if rnd.random() < mutation_rate:
            swap_idx = int(rnd.random() * len(route))
            route[swapped], route[swap_idx] = route[swap_idx], route[swapped]
    return route


def mutate_population(pop, mutation_rate):
    return [mutate(ind, mutation_rate) for ind in pop]


def next_generation(curr_pop, elite_size, mutation_rate):
    ranked = rank_routes(curr_pop)
    selected = select_mating_pool(ranked, elite_size)
    pool = mating_pool(curr_pop, selected)
    children = breed_population(pool, elite_size)
    next_gen = mutate_population(children, mutation_rate)
    return next_gen


# ------------------------------------------------------------
# Plotting
# ------------------------------------------------------------
def plot_route(route, title="Route"):
    coords = [c.coords() for c in route] + [route[0].coords()]
    coords = np.array(coords)
    plt.figure()
    plt.plot(coords[:, 0], coords[:, 1], "-o")
    for city in route:
        plt.annotate(city.cname, (city.lon, city.lat))
    plt.title(title)
    plt.show()


# ------------------------------------------------------------
# GA with progress tracking
# ------------------------------------------------------------
def run_ga(cities, pop_size, elite_size, mutation_rate, generations):
    population = init_population(pop_size, cities)
    progress_best = []
    progress_avg = []

    print("Initial distance:", 1 / rank_routes(population)[0][1])

    for gen in range(generations):
        population = next_generation(population, elite_size, mutation_rate)
        ranked = rank_routes(population)

        best_dist = 1 / ranked[0][1]
        avg_fit = np.mean([fit for _, fit in ranked])

        progress_best.append(best_dist)
        progress_avg.append(avg_fit)

        if gen % 10 == 0:  # plot intermediate route
            best_route_idx = ranked[0][0]
            plot_route(population[best_route_idx], f"Generation {gen}")

    print("Final distance:", progress_best[-1])
    best_route_idx = rank_routes(population)[0][0]
    best_route = population[best_route_idx]

    # plot fitness progress
    plt.figure()
    plt.plot(progress_best, label="Best Distance")
    plt.plot([1 / f for f in progress_avg], label="Avg Distance (from fitness)")
    plt.xlabel("Generation")
    plt.ylabel("Distance")
    plt.legend()
    plt.title("GA Progress")
    plt.show()

    return best_route


# ------------------------------------------------------------
# Main MS2513_TSP_GA.py
# ------------------------------------------------------------
if __name__ == "__main__":
    city_data = read_city_file()
    print("\nNumber of Cities:", len(city_data))

    best = run_ga(
        cities=city_data,
        pop_size=100,
        elite_size=20,
        mutation_rate=0.01,
        generations=100,
    )

    plot_route(best, "Best Route (Final)")