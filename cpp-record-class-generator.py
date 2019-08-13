#!/bin/env python
import os
import sys
from shutil import copyfile

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: {0} in_file out_file table_name".format(sys.argv[0]))

    in_file_path = sys.argv[1]
    out_file_path = sys.argv[2]
    table_name = sys.argv[3]

    with open(out_file_path, 'w', encoding="utf-8-sig") as out_file:
        with open(in_file_path, 'r', encoding="utf-8-sig") as in_file:
            column_raw_names = in_file.readline().rstrip('\n').split(",")
            column_count = len(column_raw_names)

            column_names = in_file.readline().rstrip('\n')\
                .replace('{', '').replace('}', '')\
                .replace('[', '').replace(']', '')\
                .replace('<', '').replace('>', '').split(",")

            column_types = in_file.readline().rstrip('\n').split(",")

            header_names = ""
            header_vars = ""
            for column_name, column_raw_name in zip(column_names, column_raw_names):
                header_names += "            , \"{0}\"\n".format(column_raw_name)
                header_vars += "            {0} {1}_\n".format( "," if len(header_vars) > 0 else "", "id" if len(header_vars) == 0 else (column_name if len(column_name) > 0 else "c{0}".format(column_raw_name)))

            variable_defs = ""
            using_defs = ""
            seen_types = set()
            for column_type, column_name, column_raw_name in zip(column_types, column_names, column_raw_names):
                if column_type == "str":
                    column_type = "std::string"
                elif column_type == "int64":
                    column_type = "StringInt64"
                elif column_type == "uint64":
                    column_type = "StringInt64"
                elif column_type == "int32":
                    column_type = "int32_t"
                elif column_type == "uint32":
                    column_type = "uint32_t"
                elif column_type == "int16":
                    column_type = "int16_t"
                elif column_type == "uint16":
                    column_type = "uint16_t"
                elif column_type == "byte":
                    column_type = "uint8_t"
                elif column_type == "sbyte":
                    column_type = "int8_t"
                elif column_type.startswith("bit"):
                    column_type = "StringBool"
                elif column_type not in seen_types:
                    seen_types.add(column_type)
                    using_defs += "    using {0} = int32_t;\n".format(column_type)
                variable_defs += "    {0} {1}_;\n".format(column_type, "id" if len(variable_defs) == 0 else (column_name if len(column_name) > 0 else "c{0}".format(column_raw_name)))

        with open("./cpp-record-class-template.h", 'r', encoding="utf-8-sig") as in_file:
            data = in_file.read()
            data = data.format(table_name,column_count, using_defs, header_names, header_vars, variable_defs)
            out_file.write(data)
