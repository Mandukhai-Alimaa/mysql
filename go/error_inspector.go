// Copyright (c) 2025 ADBC Drivers Contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//         http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package mysql

import (
	"errors"

	"github.com/adbc-drivers/driverbase-go/driverbase"
	"github.com/apache/arrow-adbc/go/adbc"
	"github.com/go-sql-driver/mysql"
)

// MySQLErrorInspector extracts error information from MySQL driver errors
type MySQLErrorInspector struct{}

// InspectError examines a MySQL error and extracts metadata
func (m MySQLErrorInspector) InspectError(err error, defaultStatus adbc.Status) driverbase.ErrorInfo {
	info := driverbase.ErrorInfo{Status: defaultStatus}

	var mysqlErr *mysql.MySQLError
	if errors.As(err, &mysqlErr) {
		// Extract vendor code
		info.VendorCode = int32(mysqlErr.Number)

		// Extract SQLSTATE
		info.SqlState = string(mysqlErr.SQLState[:])

		// Map MySQL error codes to ADBC status codes
		switch mysqlErr.Number {
		// Authentication errors
		case 1045: // ER_ACCESS_DENIED_ERROR
			info.Status = adbc.StatusUnauthenticated
		case 1044, 1142, 1143, 1227: // Permission errors
			info.Status = adbc.StatusUnauthorized

		// Not found errors
		case 1146: // ER_NO_SUCH_TABLE
			info.Status = adbc.StatusNotFound
		case 1049: // ER_BAD_DB_ERROR
			info.Status = adbc.StatusNotFound

		// Already exists errors
		case 1050: // ER_TABLE_EXISTS_ERROR
			info.Status = adbc.StatusAlreadyExists
		case 1007: // ER_DB_CREATE_EXISTS
			info.Status = adbc.StatusAlreadyExists

		// Integrity constraint violations
		case 1062: // ER_DUP_ENTRY
			info.Status = adbc.StatusIntegrity
		case 1451: // ER_ROW_IS_REFERENCED_2 (foreign key constraint)
			info.Status = adbc.StatusIntegrity
		case 1452: // ER_NO_REFERENCED_ROW_2 (foreign key constraint)
			info.Status = adbc.StatusIntegrity
		case 1048: // ER_BAD_NULL_ERROR
			info.Status = adbc.StatusIntegrity
		case 1364: // ER_NO_DEFAULT_FOR_FIELD
			info.Status = adbc.StatusIntegrity

		// Invalid argument / syntax errors
		case 1064: // ER_PARSE_ERROR
			info.Status = adbc.StatusInvalidArgument
		case 1054: // ER_BAD_FIELD_ERROR
			info.Status = adbc.StatusInvalidArgument
		case 1052: // ER_NON_UNIQ_ERROR
			info.Status = adbc.StatusInvalidArgument

		// Data errors
		case 1366: // ER_TRUNCATED_WRONG_VALUE_FOR_FIELD
			info.Status = adbc.StatusInvalidData
		case 1292: // ER_TRUNCATED_WRONG_VALUE
			info.Status = adbc.StatusInvalidData
		case 1264: // ER_WARN_DATA_OUT_OF_RANGE
			info.Status = adbc.StatusInvalidData

		// Timeout / cancellation
		case 1205: // ER_LOCK_WAIT_TIMEOUT
			info.Status = adbc.StatusTimeout
		case 1213: // ER_LOCK_DEADLOCK
			info.Status = adbc.StatusCancelled

		// Connection / IO errors
		case 2002, 2003, 2006, 2013: // Various connection errors
			info.Status = adbc.StatusIO

		// Internal errors
		case 1105: // ER_UNKNOWN_ERROR
			info.Status = adbc.StatusInternal
		}

		// Also check SQLSTATE prefix for additional mappings
		if len(info.SqlState) >= 2 {
			switch info.SqlState[:2] {
			case "28": // Invalid authorization
				if info.Status == defaultStatus {
					info.Status = adbc.StatusUnauthenticated
				}
			case "42": // Syntax error or access rule violation
				if info.Status == defaultStatus {
					info.Status = adbc.StatusInvalidArgument
				}
			case "23": // Integrity constraint violation
				if info.Status == defaultStatus {
					info.Status = adbc.StatusIntegrity
				}
			case "HY": // General error
				// Keep the more specific mapping if we already set one
			}
		}
	}

	return info
}
