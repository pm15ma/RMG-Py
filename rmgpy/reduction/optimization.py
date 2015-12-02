#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
#
#   RMG - Reaction Mechanism Generator
#
#   Copyright (c) 2002-2010 Prof. William H. Green (whgreen@mit.edu) and the
#   RMG Team (rmg_dev@mit.edu)
#
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the 'Software'),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#
################################################################################

import numpy as np

from reduction import reduce_model
from rmgpy.scoop_framework.util import logger as logging

def optimize(target_label, reactionModel, rmg, reaction_system_index, error, orig_observable):
    """
    The optimization algorithm that searches for the most reduced model that satisfies the
    applied constraints.

    The error introduced by the reduced model for a response variable
    of a target is used as the objective function.

    The optimization algorithm increments the trial tolerance from a very low value
    until the introduced error is greater than the user-provided threshold.
    """


    start = 1E-20
    incr = 10
    tolmax = 1

    """
    Tolerance to decide whether a reaction is unimportant for the formation/destruction of a species

    Tolerance is a floating point value between 0 and 1.

    A high tolerance means that many reactions will be deemed unimportant, and the reduced model will be drastically
    smaller.

    A low tolerance means that few reactions will be deemed unimportant, and the reduced model will only differ from the full
    model by a few reactions.
    """
    tol = start
    trial = start

    important_reactions = reactionModel.core.reactions
    
    while True:
        logging.info('Trial tolerance: {trial:.2E}'.format(**locals()))
        reduced_observable, new_important_reactions = reduce_model(trial, target_label, reactionModel, rmg, reaction_system_index)
        
        devs = compute_deviation(orig_observable, reduced_observable)

        if np.any(devs > error) or trial > tolmax:
            break

        tol = trial
        trial = trial * incr
        important_reactions = new_important_reactions

    if tol == start:
        logging.error('Starting value for tolerance was too high...')

    return tol, important_reactions

def compute_deviation(original, reduced):
    """
    Computes the relative deviation between the observables of the
    original and reduced model.

    Assumes the observables are numpy arrays.
    """
    devs = np.abs((reduced - original) / original)

    logging.info('Deviations: '.format())
    for dev in devs:
        logging.info('{:.2f}%'.format(dev * 100))

    return devs