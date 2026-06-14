"""Evolutionary algorithm implementation."""

import random
from typing import Callable, List, Optional
import numpy as np


class Individual:
    """Represents a single individual in the population.
    
    Attributes:
        chromosome: The genetic material (array of values)
        fitness: Fitness value (None until evaluated)
    """
    
    def __init__(self, chromosome: np.ndarray):
        """Initialize an individual with a chromosome.
        
        Args:
            chromosome: 1D array representing the individual's genes
        """
        self.chromosome = chromosome.copy()
        self.fitness: Optional[float] = None
    
    def mutate(self, mutation_rate: float) -> None:
        """Apply mutation to chromosome.
        
        Args:
            mutation_rate: Probability of each gene being mutated (0-1)
        """
        for i in range(len(self.chromosome)):
            if random.random() < mutation_rate:
                self.chromosome[i] += np.random.normal(0, 0.1)
    
    def __repr__(self) -> str:
        fitness_str = f"{self.fitness:.6f}" if self.fitness else "unevaluated"
        return f"Individual(fitness={fitness_str}, genes={len(self.chromosome)})"


class Population:
    """Manages a population of individuals.
    
    Attributes:
        size: Population size
        individuals: List of Individual objects
        champion_idx: Index of best individual
        generation: Current generation number
    """
    
    def __init__(self, size: int, chromosome_size: int):
        """Initialize a population with random individuals.
        
        Args:
            size: Number of individuals in population
            chromosome_size: Size of each chromosome
        """
        self.size = size
        self.individuals: List[Individual] = [
            Individual(np.random.randn(chromosome_size)) for _ in range(size)
        ]
        self.champion_idx = 0
        self.generation = 0
    
    def evaluate(self, fitness_func: Callable[[np.ndarray], float]) -> None:
        """Evaluate fitness for all individuals.
        
        Args:
            fitness_func: Function that takes chromosome and returns fitness
        """
        for ind in self.individuals:
            ind.fitness = fitness_func(ind.chromosome)
        
        self.champion_idx = max(
            range(len(self.individuals)),
            key=lambda i: self.individuals[i].fitness or 0.0
        )
    
    def get_champion(self) -> Individual:
        """Get the best individual in population.
        
        Returns:
            Best individual
        """
        return self.individuals[self.champion_idx]
    
    def select_best(self, k: int) -> List[Individual]:
        """Select k best individuals.
        
        Args:
            k: Number of individuals to select
            
        Returns:
            List of k best individuals
        """
        sorted_pop = sorted(
            self.individuals,
            key=lambda x: x.fitness or 0.0,
            reverse=True
        )
        return sorted_pop[:min(k, len(sorted_pop))]
    
    @staticmethod
    def crossover(parent1: Individual, parent2: Individual) -> Individual:
        """Create offspring via uniform crossover.
        
        Args:
            parent1: First parent individual
            parent2: Second parent individual
            
        Returns:
            Offspring individual
        """
        offspring_genes = np.where(
            np.random.rand(len(parent1.chromosome)) < 0.5,
            parent1.chromosome,
            parent2.chromosome
        )
        return Individual(offspring_genes)


class EvolutionaryAlgorithm:
    """Main evolutionary algorithm driver.
    
    Attributes:
        population_size: Number of individuals per generation
        generations: Number of generations to run
        mutation_rate: Probability of gene mutation
        elite_size: Number of elite individuals to preserve
        population: Current population
        best_fitness_history: History of best fitness per generation
    """
    
    def __init__(
        self,
        population_size: int,
        generations: int,
        mutation_rate: float = 0.2,
        elite_size: Optional[int] = None
    ):
        """Initialize evolutionary algorithm.
        
        Args:
            population_size: Number of individuals per generation
            generations: Number of generations to run
            mutation_rate: Mutation probability (0-1)
            elite_size: Number of elite individuals (default: population_size/2)
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size or population_size // 2
        self.population: Optional[Population] = None
        self.best_fitness_history: List[float] = []
    
    def run(
        self,
        model_template: np.ndarray,
        fitness_func: Callable[[np.ndarray], float],
        report_func: Optional[Callable[[int, np.ndarray], None]] = None
    ) -> np.ndarray:
        """Run evolutionary algorithm.
        
        Args:
            model_template: Initial chromosome template
            fitness_func: Function to evaluate fitness
            report_func: Optional function to report each generation
            
        Returns:
            Best solution found
        """
        chromosome_size = len(model_template)
        self.population = Population(self.population_size, chromosome_size)
        self.best_fitness_history = []
        
        for gen in range(self.generations):
            self.population.evaluate(fitness_func)
            champion = self.population.get_champion()
            self.best_fitness_history.append(champion.fitness)
            
            if report_func:
                report_func(gen, champion.chromosome)
            
            print(
                f"Generation {gen:4d}: Best Fitness = {champion.fitness:.6f}"
            )
            
            elite = self.population.select_best(self.elite_size)
            
            new_population = [
                Individual(ind.chromosome.copy()) for ind in elite
            ]
            
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(elite, 2)
                offspring = self.population.crossover(parent1, parent2)
                offspring.mutate(self.mutation_rate)
                new_population.append(offspring)
            
            self.population.individuals = new_population[:self.population_size]
            self.population.generation = gen + 1
        
        self.population.evaluate(fitness_func)
        champion = self.population.get_champion()
        return champion.chromosome
