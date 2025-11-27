import sys
import os
import pytest
import tempfile
import csv
from Gateway.providers.provider import Provider

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_csv():
    content = "timestamp,symbol,price\n2025-10-01 09:30:00,AAPL,169.89\n2025-10-01 09:30:01,MSFT,320.22\n"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write(content)
        f.flush()
        fname = f.name
    yield fname
    os.unlink(fname)

class MockProvider(Provider):
    def __init__(self, data_list):
        self.data_list = data_list
        self.index = 0
    
    def get_next_data(self):
        if self.index < len(self.data_list):
            result = self.data_list[self.index]
            self.index += 1
            return result
        return None

@pytest.fixture
def mock_provider():
    return MockProvider([b"test1", b"test2"])

@pytest.fixture
def empty_mock_provider():
    return MockProvider([])

