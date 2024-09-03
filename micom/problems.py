"""Implements tradeoff optimization between community and egoistic growth."""

from cobra.util import interface_to_str
from micom.util import (
    _format_min_growth,
    _apply_min_growth,
    check_modification,
    get_context,
    reset_min_community_growth,
)
from micom.logger import logger
from micom.solution import (
    solve,
    crossover,
    optimize_with_retry,
    optimize_with_fraction,
)
from optlang.symbolics import Zero
from optlang.interface import OPTIMAL
from collections.abc import Sized
from functools import partial
import pandas as pd
import numpy as np
from rich.progress import track
from micom import data
import statistics
from micom.optcom import add_moma_optcom

def regularize_l2_norm(community, min_growth):
    """Add an objective to find the most "egoistic" solution.

    This adds an optimization objective finding a solution that maintains a
    (sub-)optimal community growth rate but is the closest solution to the
    community members individual maximal growth rates. So it basically finds
    the best possible tradeoff between maximizing community growth and
    individual (egoistic) growth. Here the objective is given as the sum of
    squared differences between the individuals current and maximal growth
    rate. In the linear case squares are substituted by absolute values
    (Manhattan distance).

    Arguments
    ---------
    community : micom.Community
        The community to modify.
    min_growth : positive float
        The minimal community growth rate that has to be mantained.
    linear : boolean
        Whether to use a non-linear (sum of squares) or linear version of the
        cooperativity cost. If set to False requires a QP-capable solver.
    max_gcs : None or dict
        The precomputed maximum individual growth rates.

    """
    logger.info("adding L2 norm to %s" % community.id)
    l2 = Zero
    l3 = Zero
    community.variables.community_objective.lb = min_growth
    context = get_context(community)
    if context is not None:
        context(partial(reset_min_community_growth, community))
    ex_comunity = community.variables.community_objective
    for sp in range(len(community.taxa)):
        for j in range(sp + 1, len(community.taxa)):
            #adding new constrain
            const_sp=community.constraints["objective_" + community.taxa[sp]]
            const_j=community.constraints["objective_" + community.taxa[j]]
            ex_sp = sum(v for v in const_sp.variables if (v.ub - v.lb) > 1e-6)
            ex_j = sum(v for v in const_j.variables if (v.ub - v.lb) > 1e-6)
            ex_spj = ex_sp - ex_j
            #retrieving distance_value
            similarity_value=1
    #version1 just adding our term
            if similarity_value>0:
                l2 += ((similarity_value * ex_spj)**2).expand()
    l3=ex_comunity -(0.1 * l2)
    community.objective = -l3
    community.modification = "l2 regularization"
    logger.info("finished adding tradeoff objective to %s" % community.id)


def cooperative_tradeoff(community, min_growth, fraction, fluxes, pfba, atol, rtol):
    """Find the best tradeoff between community and individual growth."""
    with community as com:
        solver = interface_to_str(community.problem)
        check_modification(community)
        min_growth = _format_min_growth(min_growth, community.taxa)
        _apply_min_growth(community, min_growth)

        com.objective = com.scale * com.variables.community_objective
        min_growth = (
            optimize_with_retry(com, message="could not get community growth rate.")
            / com.scale
        )
        if not isinstance(fraction, Sized):
            fraction = [fraction]
        else:
            fraction = np.sort(fraction)[::-1]

        # Add needed variables etc.
        regularize_l2_norm(com, 0.0)
#        p,term2,term1=regularize_l2_norm(com, 0.0)
#        fra=1
#        term2=fra* term2
        results = []
        for fr in fraction:
#            term1=fr* term1
#            ex = (p - term2 - term1)**2
#            community.objective = -ex
            com.variables.community_objective.lb = fr * min_growth
            com.variables.community_objective.ub = min_growth
            sol = solve(community, fluxes=fluxes, pfba=pfba, atol=atol, rtol=rtol)
            # OSQP is better with QPs then LPs
            # so it won't get better with the crossover
            if not pfba and sol.status != OPTIMAL and solver != "osqp":
                sol = crossover(
                    com, sol, fluxes=fluxes
                )
            results.append((fr, sol))
        if len(results) == 1:
            return results[0][1]
        return pd.DataFrame.from_records(results, columns=["tradeoff", "solution"])


def knockout_taxa(community, taxa, fraction, method, progress, diag=True):
    """Knockout a taxon from the community."""
    with community as com:
        check_modification(com)
        min_growth = _format_min_growth(0.0, com.taxa)
        _apply_min_growth(com, min_growth)

        com.objective = com.scale * com.variables.community_objective
        community_min_growth = (
            optimize_with_retry(com, "could not get community growth rate.") / com.scale
        )
        regularize_l2_norm(com, fraction * community_min_growth)
        old = com.optimize().members["growth_rate"]
        results = []

        iter = track(taxa, description="Knockouts") if progress else taxa
        for sp in iter:
            with com:
                logger.info("getting growth rates for %s knockout." % sp)
                [
                    r.knock_out()
                    for r in com.reactions.query(lambda ri: ri.community_id == sp)
                ]

                sol = optimize_with_fraction(com, fraction)
                new = sol.members["growth_rate"]
                if "change" in method:
                    new = new - old
                if "relative" in method:
                    new /= old
                results.append(new)

        ko = pd.DataFrame(results, index=taxa).drop("medium", 1)
        ko = ko.loc[ko.index.sort_values(), ko.columns.sort_values()]
        if not diag:
            np.fill_diagonal(ko.values, np.NaN)

        return ko
