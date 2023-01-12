# pytest-ticket

This is a `pytest` plugin that adds the ability to filter test cases by
associated ticket of a tracker of your choice.

It adds:
* `ticket_tools` option to `[pytest]` section of `pytest.ini` to define ticket
  tools (or trackers) of your choice
* `@pytest.mark.ticket` mark to associate test case with one or more tickets
* `--ticket` command line option to filter out test cases that are not
  associated with selected ticket(s)

## Example usage

1. Enable plugin in conftest.py

    ```python
    pytest_plugins = (
        "pytest_ticket",
    )
    ```

2. Define trackers in pytest.ini (comma-separated list)

    ```ini
    [pytest]
    ticket_tools = bz,gh
    ```

3. Define test with ticket mark

    ```python
    @pytest.mark.ticket(gh=1001, bz=[2001, 2002])
    def test_ticket():
        pass
    ```

4. Run pytest with ticket filter

    ```
    $ pytest --ticket=gh#1001
    ```

## Ticket mark

The ticket mark takes one or more keyword arguments as configured in pytest.ini
`ticket_tools` option, each argument can take a single value or list of values.

```
@pytest.mark.ticket(tool=int | str | list[int | str], ...)
```

## --ticket command line option

You can filter tests using the `--ticket` option, which takes `tool#ticket` as
an argument. This option can be passed multiple times.

```
pytest --ticket=tool#id --ticket=tool2#id2 ...
```