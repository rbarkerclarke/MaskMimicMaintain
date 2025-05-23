import numpy as np
import statistics as stat
import pandas as pd
import seaborn as sns
import random
from itertools import *
try:
    import itertools.izip as zip
except ImportError:
    import itertools


def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

def get_mutation_count(pop, mu,seq_length=1):
    N=sum(pop.values())
    mean = mu * N * seq_length
    return np.random.poisson(mean)

def get_random_haplotype(pop, generations=100):
    pop_size=sum(pop.values())
    haplotypes = list(pop.keys())
    frequencies = [x/float(pop_size) for x in pop.values()]
    total = sum(frequencies)
    frequencies = [x / total for x in frequencies]
    return np.random.choice(haplotypes, p=frequencies)

def get_mutant(pop, haplotype, seq_length=1, alphabet = ['0','1'], base_haplotype = "0"):
    site = np.random.randint(seq_length)
    possible_mutations = list(alphabet)
    possible_mutations.remove(haplotype[site])
    mutation = np.random.choice(possible_mutations)
    new_haplotype = haplotype[:site] + mutation + haplotype[site+1:]
    return new_haplotype


def mutation_event(pop):
    haplotype = get_random_haplotype(pop)
    if pop[haplotype] > 1:
        pop[haplotype] -= 1
        new_haplotype = get_mutant(pop, haplotype)
        if new_haplotype in pop:
            pop[new_haplotype] += 1
        else:
            pop[new_haplotype] = 1

def mutation_step(pop,mu):
    mutation_count = get_mutation_count(pop,mu)
    for i in range(mutation_count):
        mutation_event(pop)


def get_fitness(awm, amw, s, frequencies,pop, generations=100):
    pop_size=sum(pop.values())
    payoff=[[1, 1+awm], [1+s+amw, 1+s]]
    x = frequencies
    f = np.dot(payoff,x)
    fitness = {'0':f[0], '1':f[1]}
    #print(f"fitness {pop}")
    return fitness


def get_offspring_counts(s,x,y,pop):
    pop_size=sum(pop.values())
    haplotypes = list(pop.keys())
    frequencies = [pop[haplotype]/float(pop_size) for haplotype in haplotypes]
    fitness = get_fitness(x,y,s,frequencies,pop)
    fitnesses = [fitness[haplotype] for haplotype in haplotypes]
    weights = [x * y for x,y in zip(frequencies, fitnesses)]
    total = sum(weights)
    weights = [x / total for x in weights]
    #print(weights)
    #print(f"offspring {pop} and {pop_size}")
    return list(np.random.multinomial(pop_size, weights))


def offspring_step(s,x,y,pop):
    haplotypes = list(pop.keys())
    counts = get_offspring_counts(s,x,y,pop)
    #print(counts)
    for (haplotype, count) in zip(haplotypes, counts):
        if (count > 0):
            pop[haplotype] = count
        else:
            pop[haplotype] = 0

def time_step(s,x,y,pop, mu):
    mutation_step(pop, mu)
    offspring_step(s,x,y,pop)


def simulate(s,x,y,pop, mu, generations=100):
    pop_size=sum(pop.values())
    history = []
    clone_pop = dict(pop)
    history.append(clone_pop)
    for i in range(generations):
        time_step(s,x,y,pop, mu)
        clone_pop = dict(pop)
        history.append(clone_pop)
    return(history)

def maintain_0(awm, s):
    amw = awm = 0
    return(amw)

def mask_0(awm, s):
    amw = awm -2*s
    return(amw)

def mimic_0(awm, s):
    amw = -s/(1+s)
    return(amw)


def maintain_1(amw, s, mu):
    awm = mu*amw/(s*(1+s))
    return(awm)

def mask_1(amw, s, mu):
    awm = 2*s + amw
    return(awm)

def mimic_1(amw, s, mu):
    awm = -s/(1+s) + (-s + amw)*mu/(s*(1+s))
    return(awm)
