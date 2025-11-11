# Copyright (c) 2025 Columnar Technologies Inc.  All rights reserved.

import os

import pytest


def pytest_generate_tests(metafunc) -> None:
    metafunc.parametrize(
        "driver",
        [pytest.param("mysql:", id="mysql")],
        scope="module",
        indirect=["driver"],
    )


@pytest.fixture(scope="session")
def mysql_host() -> str:
    """MySQL host. Example: MYSQL_HOST=localhost"""
    return os.environ.get("MYSQL_HOST", "localhost")


@pytest.fixture(scope="session")
def mysql_port() -> str:
    """MySQL port. Example: MYSQL_PORT=3307"""
    return os.environ.get("MYSQL_PORT", "3306")


@pytest.fixture(scope="session")
def mysql_database() -> str:
    """MySQL database name. Example: MYSQL_DATABASE=db"""
    return os.environ.get("MYSQL_DATABASE", "db")


@pytest.fixture(scope="session")
def creds() -> tuple[str, str]:
    """MySQL credentials. Example: MYSQL_USERNAME=my MYSQL_PASSWORD=password"""
    username = os.environ.get("MYSQL_USERNAME", "my")
    password = os.environ.get("MYSQL_PASSWORD", "password")
    return username, password


@pytest.fixture(scope="session")
def uri(mysql_host: str, mysql_port: str, mysql_database: str) -> str:
    """
    Constructs a clean MySQL URI without credentials.
    Example: mysql://localhost:3306/db
    """
    return f"mysql://{mysql_host}:{mysql_port}/{mysql_database}"


@pytest.fixture(scope="session")
def dsn(creds: tuple[str, str], mysql_host: str, mysql_port: str, mysql_database: str) -> str:
    """
    Constructs a MySQL DSN in Go MySQL Driver's native format.
    Example: my:password@tcp(localhost:3306)/db
    """
    username, password = creds
    return f"{username}:{password}@tcp({mysql_host}:{mysql_port})/{mysql_database}"


@pytest.fixture(scope="session")
def mysql_socket_path() -> str:
    """
    Returns the path to MySQL Unix socket file.
    Requires a local MySQL server running with Unix socket enabled.
    Example: MYSQL_SOCKET_PATH=/tmp/mysql.sock
    """
    path = os.environ.get("MYSQL_SOCKET_PATH")
    if not path:
        pytest.skip("Must set MYSQL_SOCKET_PATH (e.g., /tmp/mysql.sock)")
    return path


