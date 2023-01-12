from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        pytest_plugins = ["pytest_ticket"]
        """
    )


def test_plugin__unknown_tracker(pytester: pytest.Pytester):
    """Make sure that unknown tracker yields error."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1234)
        def test_ticket():
            pass
        """
    )

    result = pytester.runpytest()
    result.stdout.re_match_lines(r'.*Ticket tool "tracker" is not among configured tools.*')


def test_plugin__known_tracker(pytester: pytest.Pytester):
    """Make sure that known tracker works correctly."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1234)
        def test_1():
            pass

        @pytest.mark.ticket(tracker="1234")
        def test_2():
            pass

        @pytest.mark.ticket(tracker=[1234])
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__filter_single_value(pytester: pytest.Pytester):
    """Make sure that filter works correctly with single value."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1234)
        def test_1():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1234")
    result.assert_outcomes(passed=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#4321")
    result.assert_outcomes(deselected=1)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")


def test_plugin__filter_multiple_values(pytester: pytest.Pytester):
    """Make sure that known tracker works with multiple values."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1234)
        def test_1():
            pass

        @pytest.mark.ticket(tracker=4321)
        def test_2():
            pass

        @pytest.mark.ticket(tracker=1111)
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1234", "--ticket=tracker#4321")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1111")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__filter_multiple_values_list(pytester: pytest.Pytester):
    """Make sure that known tracker works with multiple values for single test."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=[1234, 4321])
        def test_1():
            pass

        @pytest.mark.ticket(tracker=4321)
        def test_2():
            pass

        @pytest.mark.ticket(tracker=1111)
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1234", "--ticket=tracker#4321")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#4321")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1111")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__filter_multiple_values_list_string(pytester: pytest.Pytester):
    """Make sure that known tracker works with multiple string values for single test."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=["1234", "4321"])
        def test_1():
            pass

        @pytest.mark.ticket(tracker="4321")
        def test_2():
            pass

        @pytest.mark.ticket(tracker="1111")
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1234", "--ticket=tracker#4321")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#4321")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1111")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__filter_multiple_trackers(pytester: pytest.Pytester):
    """Make sure that known tracker works with multiple trackers."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = bz,gh
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(bz=1111, gh=2111)
        def test_1():
            pass

        @pytest.mark.ticket(bz=1112, gh=2112)
        def test_2():
            pass

        @pytest.mark.ticket(bz="1113")
        def test_3():
            pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=3)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=bz#1111")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=gh#2111")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=bz#1111", "--ticket=gh#2112")
    result.assert_outcomes(passed=2, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")
    result.stdout.no_re_match_line(r".*test_3 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=bz#1113")
    result.assert_outcomes(passed=1, deselected=2)
    result.stdout.no_re_match_line(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
    result.stdout.re_match_lines(r".*test_3 +PASSED")


def test_plugin__class(pytester: pytest.Pytester):
    """Make sure that the mark work with classes."""
    pytester.makeini(
        """
    [pytest]
    ticket_tools = tracker
    """
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1111)
        class TestMark(object):
            @pytest.mark.ticket(tracker=1112)
            def test_1(self):
                pass

            def test_2(self):
                pass
        """
    )

    result = pytester.runpytest("-vvv")
    result.assert_outcomes(passed=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1111")
    result.assert_outcomes(passed=2)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.re_match_lines(r".*test_2 +PASSED")

    result = pytester.runpytest("-vvv", "--ticket=tracker#1112")
    result.assert_outcomes(passed=1, deselected=1)
    result.stdout.re_match_lines(r".*test_1 +PASSED")
    result.stdout.no_re_match_line(r".*test_2 +PASSED")
