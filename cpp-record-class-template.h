#pragma once
#include "csv_table.h"

class {0}TableEntry
    : public ICsvTableEntry<{1}>
{{
public:
    using StringInt64 = std::string;
    using StringBool = std::string;
{2}
    virtual bool ReadCsvHeader(DefaultCSVReader& csv_reader) override
    {{
        csv_reader.read_header(io::ignore_extra_column
{3}
        );
        csv_reader.next_line(); // column names
        csv_reader.next_line(); // column types

        return true;
    }}

    virtual bool ReadCsvRow(DefaultCSVReader& csv_reader) override
    {{
        bool success{{
            csv_reader.read_row(
{4}
            )
        }};

        return success;
    }}

{5}
}};

