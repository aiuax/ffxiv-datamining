#pragma once
#include "csv_table.h"

class {0}TableEntry
    : public CsvTableEntry<{1}>
{{
public:
    using StringInt64 = std::string;
    using StringBool = std::string;
{2}
{4}}};

class {0}Table
    : public CsvTable<{0}TableEntry>
    , public ICsvAcceptor<{0}TableEntry>
{{
public:
    virtual bool ReadCsvHeader(DefaultCsvReader& csv_reader) override
    {{
        csv_reader.read_header(io::ignore_extra_column
{5}        );
        csv_reader.next_line(); // column names
        csv_reader.next_line(); // column types

        string_header_ = std::move(
            StringEntryArray{{
{7}            }}
        );

        return true;
    }}

    virtual bool ReadCsvRow(DefaultCsvReader& csv_reader, {0}TableEntry& out_entry) override
    {{
        bool success{{
            csv_reader.read_row(
{6}            )
        }};

        if (success)
        {{
            out_entry.string_entry_ = std::move(
                StringEntryArray{{
{3}                }}
            );
        }}

        return success;
    }}

}};

