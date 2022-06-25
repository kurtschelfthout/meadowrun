from __future__ import annotations


try:
    import eliot

    log_call = eliot.log_call
    start_action = eliot.start_action
    current_action = eliot.current_action
    preserve_context = eliot.preserve_context
    to_file = eliot.to_file
    Action = eliot.Action

except ImportError:
    from unittest.mock import Mock

    log_call = Mock()
    start_action = Mock()
    current_action = Mock()
    preserve_context = Mock()
    to_file = Mock()
    Action: Mock = Mock()  # type: ignore
