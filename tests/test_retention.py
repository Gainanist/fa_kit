"""
Unit tests for factor retention module
"""

import pytest
import numpy as np

from fa_kit import retention
from fa_kit import BrokenStick

#
# Testing number to retain calls
#

TEST_DIM = 100

TEST_DATA = sorted(np.random.randn(TEST_DIM,)**2)[::-1]
TEST_DATA /= np.sum(np.abs(TEST_DATA))


def minkept_maxdropped(vals, retain_idx):
    """Test that all the retained values are >= the dropped values"""

    min_kept = np.min([np.inf] + [
        np.abs(vals[i])
        for i in range(len(vals))
        if i in retain_idx
        ])

    max_dropped = np.max([-np.inf] + [
        np.abs(vals[i])
        for i in range(len(vals))
        if i not in retain_idx
        ])

    return min_kept, max_dropped


def test_topn_retain(top_n=7):
    """Test top n"""

    # throwing errors on garbage args
    with pytest.raises(ValueError):
        retention.retain_top_n(TEST_DATA, -1.2)


    # did we keep N?
    retain_idx = retention.retain_top_n(TEST_DATA, num_keep=top_n)
    assert len(retain_idx) == top_n
    
    # did we keep the largest?
    min_kept, max_dropped = minkept_maxdropped(TEST_DATA, retain_idx)
    assert min_kept >= max_dropped


def test_toppct_retain(keep_pct=0.9):
    """Test toppct retain"""

    # throwing errors on garbage args
    with pytest.raises(ValueError):
        retention.retain_top_pct(TEST_DATA, 1.1)

    with pytest.raises(ValueError):
        retention.retain_top_pct(TEST_DATA, 0.0)

    retain_idx = retention.retain_top_pct(TEST_DATA, keep_pct)

    # did we keep the largest?
    min_kept, max_dropped = minkept_maxdropped(TEST_DATA, retain_idx)
    assert min_kept >= max_dropped

    # test that at least `keep_pct` was retained
    kept_prop = np.sum(np.abs(TEST_DATA[retain_idx]))
    assert kept_prop >= keep_pct

    # test that we couldn't have reached `keep_pct` by retaining one fewer
    prev_kept_prop = np.sum(np.abs(TEST_DATA[retain_idx[:-1]]))
    assert prev_kept_prop < keep_pct


def test_kaiser_retain():

    # throwing errors on garbage args
    with pytest.raises(ValueError):
        retention.retain_kaiser(TEST_DATA, -1)

    retain_idx = retention.retain_kaiser(TEST_DATA, TEST_DIM)

    # did we keep the largest?
    min_kept, max_dropped = minkept_maxdropped(TEST_DATA, retain_idx)
    assert min_kept >= max_dropped

    # did we respect the cutoff?
    cutoff = 1.0 / TEST_DIM
    assert max_dropped < cutoff
    assert min_kept >= cutoff


def test_bs_retain():

    bs = BrokenStick(TEST_DATA)
    retain_idx = retention.retain_broken_stick(TEST_DATA, bs)

    # did we keep the largest?
    min_kept, max_dropped = minkept_maxdropped(TEST_DATA, retain_idx)
    assert min_kept >= max_dropped
