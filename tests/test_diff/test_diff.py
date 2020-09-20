import pytest

from baumdiff import simpletree as ST
from baumdiff import treediff
from baumdiff.matcher import IdMatcher

from ..utils import run_and_check_diff

N = ST.Node

class TestTreeDiff:
    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff1(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'), 
            N('C2', 'V2'), 
            )
        root2 = N('R', 'R', 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff2(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'), 
            N('C2', 'V2'), 
            N('C3', 'V3'), 
            )
        root2 = N('R', 'R', 
            N('C2', 'V2'), 
            N('C3', 'V3'), 
            N('C1', 'V1'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff2_progress(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'), 
            N('C2', 'V2'), 
            N('C3', 'V3'), 
            )
        root2 = N('R', 'R', 
            N('C2', 'V2'), 
            N('C3', 'V3'), 
            N('C1', 'V1'), 
            )
        class PM:
            def __init__(self):
                self._progress = 0
            def progress(self, progress):
                self._progress = progress
        matcher = IdMatcher()
        pm = PM()
        treediff.edit_script(root1, root2, matcher, pm, usemoves=usemoves)
        assert pm._progress == 4

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff3(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'), 
            N('C2', 'V2'), 
            N('C3', 'V3'), 
            )
        root2 = N('R', 'R', 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    
    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff4(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'),
            N('C2', 'V2', 
                N("C2.1", "x")), 
            N('C3', 'V3'), 
            )
        root2 = N('R', 'R', 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1', 
                N("C2.1", "x")), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff5(self, usemoves):
        root1 = N('R', 'R', 
            N('C1', 'V1'),
            N('C2', 'V2', 
                N("C2.1", "x")), 
            N('C3', 'V3'), 
            )
        root2 = N('R', 'R', 
            N("C2.1", "x"), 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff6(self, usemoves):
        root1 = N('R', 'R', 
            N("C2.1", "x"), 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        root2 = N('R', 'R', 
            N('C1', 'V1'),
            N('C2', 'V2', 
                N("C2.1", "x")), 
            N('C3', 'V3'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff7(self, usemoves):
        root1 = N('R', 'R', 
            N("C2.1", "x"), 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        root2 = N('R', 'R', 
            N('A', 'V1'),
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_diff8(self, usemoves):
        root1 = N('R', 'R', 
            N("C2.1", "x"), 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        root2 = N('R', 'R', 
            N('C1', 'V1'), 
            N('A', 'V1', N("B", "")),
            N('C3', 'V3'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    @pytest.mark.parametrize("usemoves", [True, False])
    def test_root_value_update(self, usemoves):
        root1 = N('R', 'R1', 
            N("C2.1", "x"), 
            N('C3', 'V3'), 
            N('C2', 'V2'), 
            N('C1', 'V1'), 
            )
        root2 = N('R', 'R2', 
            N('C1', 'V1'), 
            N('A', 'V1', N("B", "")),
            N('C3', 'V3'), 
            )
        run_and_check_diff(root1, root2, usemoves=usemoves)

    def test_move_subtree(self):
        root1 = N('R', 'R', 
            N("CA", "CA", 
                N('C3', 'V3'), 
                N('C2', 'V2'), 
                N('C1', 'V1'),),
            N("CB", "CB"))
        root2 = N('R', 'R', 
            N("CB", "CB",
            N("CA", "CA", 
                N('C3', 'V3'), 
                N('C2', 'V2'), 
                N('C1', 'V1'),),
            ))
        script = run_and_check_diff(root1.clone(), root2, usemoves=True)
        assert len(script) == 1
        script = run_and_check_diff(root1.clone(), root2, usemoves=False)
        assert len(script) == 2
