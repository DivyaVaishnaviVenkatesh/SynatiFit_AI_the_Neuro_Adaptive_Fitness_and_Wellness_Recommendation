import random
import pandas as pd

# Fitness function
def fitness(individual):
    return len(set(individual))

# Genetic Algorithm for optimizing workout selection
def genetic_algorithm(filtered_df):
    population_size = 10
    generations = 50
    mutation_rate = 0.1

    # Generate initial population
    population = [random.sample(list(filtered_df.iloc[:, 3:].values[0]), 7) for _ in range(population_size)]

    for _ in range(generations):
        population = sorted(population, key=lambda x: fitness(x), reverse=True)
        new_population = population[:5]

        # Crossover
        for _ in range(5):
            parent1, parent2 = random.sample(population[:5], 2)
            child = parent1[:3] + parent2[3:]
            new_population.append(child)

        # Mutation
        for individual in new_population:
            if random.random() < mutation_rate:
                idx = random.randint(0, 6)
                individual[idx] = random.choice(list(filtered_df.iloc[:, 3:].values[0]))

        population = new_population

    return population[0]
