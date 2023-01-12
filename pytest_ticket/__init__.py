from __future__ import annotations

import pytest


class TicketPlugin(object):
    def __init__(self, config: pytest.Config) -> None:
        values = map(lambda x: x.strip(), config.getini("ticket_tools").split(","))

        self.tools: list[str] = [x for x in values if x]
        self.filter: list[str] = config.getoption("ticket")

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config: pytest.Config, items: list[pytest.Item]) -> None:
        """
        Filter collected items and deselect these that do not match the ticket filter.

        :meta private:
        """
        # There is no ticket filter
        if not self.filter:
            return

        selected = []
        deselected = []

        for item in items:
            tickets = []
            for mark in item.iter_markers("ticket"):
                for key, values in mark.kwargs.items():
                    if key not in self.tools:
                        raise ValueError(
                            f'Ticket tool "{key}" is not among configured tools {self.tools}, '
                            + "add it to ticket_tools ini option"
                        )

                    values = values if isinstance(values, list) else [values]
                    for value in values:
                        tickets.append(f"{key}#{value}")

            # There was no ticket marker in this item
            if not tickets:
                if self.filter:
                    deselected.append(item)
                else:
                    selected.append(item)
                continue

            found = False
            for ticket in tickets:
                if ticket in self.filter:
                    found = True
                    break

            if found:
                selected.append(item)
            else:
                deselected.append(item)

        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


def pytest_addoption(parser: pytest.Parser):
    """
    :meta private:
    """
    parser.addini(
        "ticket_tools",
        "Comma separated list of ticket tools used by this project",
        default="",
    )
    parser.addoption(
        "--ticket",
        action="append",
        help="Filter tests by ticket (tool#id), e.g. gh#1234, can be set multiple times",
        required=False,
        default=list(),
    )


def pytest_configure(config: pytest.Config):
    """
    :meta private:
    """

    # register additional markers
    config.addinivalue_line(
        "markers",
        "ticket(bz=..., gh=..., jira=...): tickets associated with the test, the values can be either single ticket id"
        + " or list of tickets",
    )

    config.pluginmanager.register(TicketPlugin(config))
