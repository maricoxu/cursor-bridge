import pytest; from cursor_bridge.connection.strategies import ConnectionStatus; def test_basic(): assert ConnectionStatus.DISCONNECTED.value == "disconnected"
