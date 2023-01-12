from __future__ import annotations

import pytest


@pytest.fixture(autouse=True, scope="function")
def _enable_plugin(pytester: pytest.Pytester):
    pytester.makeconftest(
        """
        import pytest

        pytest_plugins = ["pytest_ticket"]
        """
    )

    pytester.makeini(
        """
        [pytest]
        ticket_tools = tracker, gh
        """
    )


def test_pytest_output__none(pytester: pytest.Pytester):
    """Make sure that no extra data is added when no ticket is set."""
    pytester.makepyfile(
        """
        import pytest

        def test_ticket(output_data_item):
            assert "pytest-ticket" not in output_data_item.extra
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__single(pytester: pytest.Pytester):
    """Make sure that extra data is added when ticket is set."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1111)
        def test_ticket(output_data_item):
            assert "pytest-ticket" in output_data_item.extra
            assert "Tickets" in output_data_item.extra["pytest-ticket"]
            assert output_data_item.extra["pytest-ticket"]["Tickets"] == "tracker#1111"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__multiple(pytester: pytest.Pytester):
    """Make sure that extra data is added when multiple tickets are set."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=[1111, 1112], gh=1113)
        def test_ticket(output_data_item):
            assert "pytest-ticket" in output_data_item.extra
            assert "Tickets" in output_data_item.extra["pytest-ticket"]
            assert output_data_item.extra["pytest-ticket"]["Tickets"] == "gh#1113, tracker#1111, tracker#1112"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_pytest_output__class(pytester: pytest.Pytester):
    """Make sure that extra data is added when ticket is set with class."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.ticket(tracker=1111)
        class TestTicket(object):
            def test_0(self, output_data_item):
                assert "pytest-ticket" in output_data_item.extra
                assert "Tickets" in output_data_item.extra["pytest-ticket"]
                assert output_data_item.extra["pytest-ticket"]["Tickets"] == "tracker#1111"

            @pytest.mark.ticket(tracker=1112)
            def test_1(self, output_data_item):
                assert "pytest-ticket" in output_data_item.extra
                assert "Tickets" in output_data_item.extra["pytest-ticket"]
                assert output_data_item.extra["pytest-ticket"]["Tickets"] == "tracker#1111, tracker#1112"
        """
    )

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)
