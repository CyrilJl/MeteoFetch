import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--full",
        action="store_true",
        default=False,
        help=(
            "Exécute la suite exhaustive : tous les paquets de chaque modèle Météo-France "
            "(potentiellement très long). Sans ce drapeau, seul un paquet représentatif par "
            "modèle est testé."
        ),
    )


@pytest.fixture(scope="session")
def full_mode(pytestconfig):
    """``True`` si pytest a été lancé avec ``--full`` (suite exhaustive)."""
    return pytestconfig.getoption("--full")
