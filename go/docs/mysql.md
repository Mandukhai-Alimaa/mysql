---
# Copyright (c) 2025 ADBC Drivers Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
{}
---

{{ cross_reference|safe }}
# MySQL Driver {{ version }}

{{ version_header|safe }}

This driver provides access to [MySQL][mysql]{target="_blank"}, a free and
open-source relational database management system.

## Installation & Quickstart

The driver can be installed with `dbc`.

To use the driver, provide the MySQL connection URI as the `url` option.

## Connection URI Format

The MySQL ADBC driver supports `mysql://` URIs:

```
mysql://[username[:password]@]host[:port][/database][?param1=value1&param2=value2]
```

Components:
- Scheme: mysql:// (required)
- Username: Optional (for authentication)
- Password: Optional (for authentication, requires username)
- Host: Required (no default)
- Port: Optional (defaults to 3306)
- Database: Optional (can be empty)
- Query params: All MySQL DSN parameters supported

See [MySQL Connection Parameters](https://dev.mysql.com/doc/refman/8.4/en/connecting-using-uri-or-key-value-pairs.html#connection-parameters-base) for complete parameter reference.

Examples:
- mysql://localhost/mydb
- mysql://user:pass@localhost:3306/mydb
- mysql://user:pass@host/db?charset=utf8mb4&timeout=30s
- mysql://user@unix(/tmp/mysql.sock)/db
- mysql://user:pass@host/

## Feature & Type Support

{{ features|safe }}

### Types

{{ types|safe }}

{{ footnotes|safe }}

[mysql]: https://www.mysql.com/
