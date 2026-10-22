import importlib
import pytest


def pytest_addoption(parser):
    parser.addoption("--impl", default="fixed", choices=["fixed", "faulty"],
                     help="which implementation to test")


@pytest.fixture(scope="session")
def impl(request):
    name = "settlement" if request.config.getoption("--impl") == "fixed" else "settlement_faulty"
    return importlib.import_module(f"rewards.{name}")
