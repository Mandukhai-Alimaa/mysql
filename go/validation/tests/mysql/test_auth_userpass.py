# Copyright (c) 2025 Columnar Technologies Inc.  All rights reserved.

import adbc_driver_manager.dbapi
import pytest
import urllib.parse
from adbc_drivers_validation import model


@pytest.mark.feature(group="Authentication", name="Username/password in URI")
def test_userpass_uri(
    driver: model.DriverQuirks,
    driver_path: str,
    uri: str,  # mysql://localhost:3306/db
    creds: tuple[str, str],
) -> None:
    """Test authentication with credentials embedded in URI."""
    username, password = creds
    parsed = urllib.parse.urlparse(uri)
    netloc = f"{username}:{password}@{parsed.netloc}"
    auth_uri = urllib.parse.urlunparse((parsed[0], netloc, *parsed[2:]))

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": auth_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")


@pytest.mark.feature(group="Authentication", name="Username/password in options")
def test_userpass_options(
    driver: model.DriverQuirks,
    driver_path: str,
    uri: str,
    creds: tuple[str, str],
) -> None:
    """Test authentication with credentials in connection options."""
    username, password = creds
    params = {
        "uri": uri,
        "username": username,
        "password": password,
    }
    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs=params,
            ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            
            
@pytest.mark.feature(group="Authentication", name="Invalid credentials in options fail")
def test_userpass_options_override_uri(
    driver: model.DriverQuirks,
    driver_path: str,
    uri: str,  # mysql://localhost:3306/db
) -> None:
    """
    Tests that 'username' and 'password' options
    override credentials in the URI.
    """
    params = {
        "uri": uri,
        "username": "this_user_is_bad",
        "password": "this_password_is_bad",
    }
    
    with pytest.raises(
        adbc_driver_manager.dbapi.OperationalError,
        match="Access denied for user 'this_user_is_bad'",
    ):
        with adbc_driver_manager.dbapi.connect(
            driver=driver_path, db_kwargs=params
        ):
            pass
        

@pytest.mark.feature(group="Security", name="SSL modes")
@pytest.mark.parametrize(
    "tls_param, expect_encrypted",
    [
        # pytest.param("tls=true", True, id="tls=true"),  # Docker MySQL container uses a self-signed certificate that fails validation.
        pytest.param("tls=skip-verify", True, id="tls=skip-verify"),
        pytest.param("tls=false", False, id="tls=false"),
        pytest.param("tls=preferred", True, id="tls=preferred"),
    ],
)
def test_ssl_modes(
    driver: model.DriverQuirks,
    driver_path: str,
    uri: str,   # mysql://localhost:3306/db
    creds: tuple[str, str],
    tls_param: str,
    expect_encrypted: bool,
) -> None:
    """Test various SSL configurations with dynamic URI construction."""
    username, password = creds

    parsed = urllib.parse.urlparse(uri)
    netloc = f"{username}:{password}@{parsed.netloc}"

    query = f"{parsed.query}&{tls_param}" if parsed.query else tls_param
    ssl_uri = urllib.parse.urlunparse((
        parsed.scheme, netloc, parsed.path,
        parsed.params, query, parsed.fragment
    ))

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": ssl_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SHOW STATUS LIKE 'Ssl_cipher'")
            result = cursor.fetchone()
            assert result, "Could not get SSL status"
            
            cipher = result[1]
            if expect_encrypted:
                assert cipher, "Ssl_cipher is empty, connection is NOT encrypted"
            else:
                assert not cipher, "Ssl_cipher is not empty, connection IS encrypted"
                

@pytest.mark.feature(group="Configuration", name="Default port")
def test_uri_default_port(
    driver: model.DriverQuirks,
    driver_path: str,
    mysql_host: str,
    mysql_database: str,
    creds: tuple[str, str],
) -> None:
    """Tests that a URI without a port connects using default 3306."""
    username, password = creds

    no_port_uri = f"mysql://{username}:{password}@{mysql_host}/{mysql_database}"
    
    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": no_port_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1


@pytest.mark.feature(group="Configuration", name="Default host and port")
def test_uri_default_host_and_port(
    driver: model.DriverQuirks,
    driver_path: str,
    mysql_database: str,
    creds: tuple[str, str],
) -> None:
    """Tests that a URI with no host/port defaults to localhost:3306."""
    username, password = creds

    no_host_uri = f"mysql://{username}:{password}@/{mysql_database}"

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": no_host_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            assert cursor.fetchone()[0] == mysql_database


@pytest.mark.feature(group="Configuration", name="Charset in URI")
def test_charset_selection_in_uri(
    driver: model.DriverQuirks,
    driver_path: str,
    uri: str,  # mysql://localhost:3306/db
    creds: tuple[str, str],
) -> None:
    """Tests that 'charset' in the URI query string is applied."""
    username, password = creds

    parsed = urllib.parse.urlparse(uri)
    netloc = f"{username}:{password}@{parsed.netloc}"
    charset_uri = urllib.parse.urlunparse((
        parsed.scheme, netloc, parsed.path,
        parsed.params, "charset=utf8mb4", parsed.fragment
    ))

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": charset_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'character_set_client'")
            result = cursor.fetchone()
            assert result
            assert result[1] == "utf8mb4"


@pytest.mark.feature(group="Configuration", name="Missing URI")
def test_missing_uri_raises_error(
    driver: model.DriverQuirks,
    driver_path: str,
) -> None:
    """Tests that connecting without a 'uri' option raises an error."""
    with pytest.raises(
        adbc_driver_manager.dbapi.ProgrammingError,
        match="missing required option uri",
    ):
        with adbc_driver_manager.dbapi.connect(
            driver=driver_path,
            db_kwargs={},
        ):
            pass


@pytest.mark.feature(group="Configuration", name="Invalid URI")
def test_invalid_uri_format(
    driver: model.DriverQuirks,
    driver_path: str,
) -> None:
    """Tests that a malformed URI raises a helpful error."""
    with pytest.raises(
        adbc_driver_manager.dbapi.ProgrammingError,
        match="invalid MySQL URI format",
    ):
        with adbc_driver_manager.dbapi.connect(
            driver=driver_path,
            db_kwargs={"uri": "mysql://[invalid-format"},
        ):
            pass


@pytest.mark.feature(group="Configuration", name="Unix socket with parentheses")
def test_unix_socket_parentheses(
    driver: model.DriverQuirks,
    driver_path: str,
    creds: tuple[str, str],
    mysql_socket_path: str, # /tmp/mysql.sock
) -> None:
    """Tests socket connection using mysql://user:pass@(/path/to/socket.sock)/db"""
    username, password = creds

    socket_uri = f"mysql://{username}:{password}@({mysql_socket_path})/db"

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": socket_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1


@pytest.mark.feature(group="Configuration", name="Unix socket with percent encoding")
def test_unix_socket_percent_encoding(
    driver: model.DriverQuirks,
    driver_path: str,
    creds: tuple[str, str],
    mysql_socket_path: str, # /tmp/mysql.sock
) -> None:
    """Tests socket connection using mysql://user:pass@/path%2Fto%2Fsocket.sock/db"""
    username, password = creds

    # Convert socket path to percent-encoded format
    # Remove leading slash and encode the path, then reconstruct
    socket_path_no_slash = mysql_socket_path[1:] if mysql_socket_path.startswith('/') else mysql_socket_path
    encoded_path = urllib.parse.quote(socket_path_no_slash, safe='')
    socket_uri = f"mysql://{username}:{password}@/{encoded_path}/db"

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": socket_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
            

# --- DSN tests ---

@pytest.mark.feature(group="Authentication", name="Basic DSN connection")
def test_basic_dsn_connection(
    driver: model.DriverQuirks,
    driver_path: str,
    dsn: str,  # Example: my:password@tcp(localhost:3306)/db
) -> None:
    """Test basic connection to MySQL using DSN format."""
    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": dsn},
            ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            
            
@pytest.mark.feature(group="Configuration", name="Minimal DSN with credentials")
def test_minimal_dsn_with_creds(
    driver: model.DriverQuirks,
    driver_path: str,
    creds: tuple[str, str],
) -> None:
    """
    Test that a minimal DSN ('user:pass@/') is valid.
    This DSN implies a connection to the default 'tcp(localhost:3306)'.
    """
    username, password = creds
    
    minimal_uri = f"{username}:{password}@/"
    
    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": minimal_uri},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            assert result[0] is None


@pytest.mark.feature(group="Configuration", name="Plain hostname with credentials in options")
def test_plain_host_with_creds_options(
    driver: model.DriverQuirks,
    driver_path: str,
    creds: tuple[str, str],
) -> None:
    """
    Tests that a plain host string
    is correctly combined with credentials from options.
    """
    username, password = creds

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": "localhost", "username": username, "password": password},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1


@pytest.mark.feature(group="Authentication", name="Native DSN with options override")
def test_native_dsn_options_override(
    driver: model.DriverQuirks,
    driver_path: str,
    dsn: str, # Example: my:password@tcp(localhost:3306)/db
) -> None:
    """
    Tests that 'username' and 'password' options
    override credentials in a NATIVE DSN (not a URI).
    """
    params = {
        "uri": dsn, # Has valid credentials
        "username": "this_user_is_bad",
        "password": "this_password_is_bad",
    }
    
    with pytest.raises(
        adbc_driver_manager.dbapi.OperationalError,
        match="Access denied for user 'this_user_is_bad'",
    ):
        with adbc_driver_manager.dbapi.connect(
            driver=driver_path, db_kwargs=params
        ):
            pass


@pytest.mark.feature(group="Configuration", name="Unix socket DSN")
def test_unix_socket_dsn(
    driver: model.DriverQuirks,
    driver_path: str,
    creds: tuple[str, str],
    mysql_socket_path: str,  # Example: /tmp/mysql.sock
) -> None:
    """Tests socket connection using native DSN format: user:pass@unix(/path/to/socket.sock)/db"""
    username, password = creds

    socket_dsn = f"{username}:{password}@unix({mysql_socket_path})/db"

    with adbc_driver_manager.dbapi.connect(
        driver=driver_path,
        db_kwargs={"uri": socket_dsn},
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1