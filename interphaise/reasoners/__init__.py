"""LLM reasoners: the decisions a computational scientist makes by judgement.

  interphase_reasoner  — sharp interface or interphase? which layers, in which order?
  facet_reasoner       — which facets are in contact?
  judge                — is the relaxed model physically acceptable?

Each takes an ``llm(system, user)`` callable, samples it several times, and
returns the consensus with its agreement fraction.
"""
