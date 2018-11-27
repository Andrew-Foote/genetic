# -*- coding: utf-8 -*-
"""
Created on Sun Mar  5 02:30:29 2017

@author: Andrew Foote

Functions for running simple genetic algorithms with one chromosome of fixed
length, with uniform probability of crossover of its length, and fitness-
proportionate parent selection probability.
"""

import numpy as np

def randpop(popsize, genomesize):
    return np.random.randint(2, size=(popsize, genomesize)).astype(bool)

def mutate(pop, p):
    """Mutate the organisms in pop. Each bit in each organism's genome has
    probability p of being mutated and replaced with a randomly-chosen bit
    (i.e. probability p/2 of being changed)."""
    pop ^= np.random.binomial(1, p/2, size=pop.shape).astype(bool)
    
def regen(pop, fitnessdist, crossover_p, mutate_p):
    """Generate a new population by mating the organisms in pop. The new
    population is the same size as the old one, and each pair of its members
    is generated by selecting two parents from the old population, with the
    probability of a given member of the old population being selected as one
    of the parents being proportional to its fitness as given by fitnessdist.
    The parents' chromosomes are copied, crossed over with probability
    crossover_p, and mutated with probability mutate_p at each locus."""
    popsize = pop.shape[0]
    genomesize = pop.shape[1]
    newpop = pop[np.random.choice(np.arange(popsize),
                                  p=fitnessdist/np.sum(fitnessdist),
                                  size=popsize), :]
    halfpopsize = popsize // 2
    crossover_indices = np.random.binomial(1, crossover_p, size=halfpopsize).astype(bool)
    ncrossovers = np.count_nonzero(crossover_indices)
    crossover_loci = np.random.randint(genomesize, size=ncrossovers)
    i = 0
    for j in range(0, popsize, 2):
        if crossover_indices[j // 2]:
            locus = crossover_loci[i]
            head1 = newpop[j, locus:].copy()
            head2 = newpop[j + 1, locus:].copy()
            newpop[j, locus:], newpop[j + 1, locus:] = head2, head1
            i += 1
    mutate(newpop, mutate_p)
    return newpop

def evolve(pop, ngens, crossoverp, mutatep, fitnessf, dataf=None, **kwargs):
    if dataf is None:
        def dataf(pop, **kwargs):
            return np.mean(kwargs['fitnessdist'])
    kwargs['fitnessdist'] = fitnessf(pop, **kwargs)
    data = [dataf(pop, **kwargs)]
    for i in range(ngens):
        if i > 0 and i % 10 == 0:
            print("generation", i)
        pop = regen(pop, kwargs['fitnessdist'], crossoverp, mutatep)
        kwargs['fitnessdist'] = fitnessf(pop, **kwargs)
        data.append(dataf(pop, **kwargs))
    return data

# example fitness functions

def hammingweight(pop):
    return np.sum(pop, axis=1) + 1

def hammingdistance(pop, genome):
    return np.sum(pop ^ genome, axis=1) + 1

def mutualhammingdistance(pop):
    def f(org):
        return np.mean(hammingdistance(pop, org))
    return np.apply_along_axis(f, 1, pop)

def asinteger(pop):
    return pop @ 2 ** np.arange(pop.shape[1] - 1, -1, -1) + 1

pdpayoff = np.array([[1, 3], [0, 2]])

def memorylesspd(pop, genome):
    def f(org):
        return np.sum(pdpayoff[org.astype(int), genome.astype(int)])
    return np.apply_along_axis(f, 1, pop)

def memorylessmutualpd(pop):
    def f(org):
        return np.mean(memorylesspd(pop, org))
    return np.apply_along_axis(f, 1, pop)