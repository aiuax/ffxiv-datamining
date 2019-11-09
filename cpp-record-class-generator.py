#!/bin/env python
import os
import sys
import re
from shutil import copyfile

def fixup_csv_file(in_file_path):
    leaf = os.path.split(in_file_path)[1]
    out_file_path = "./{0}.temp".format(leaf)
    modified = False
    with open(out_file_path, 'w', encoding="utf-8-sig") as out_file:
        with open(in_file_path, 'r', encoding="utf-8-sig") as in_file:
            line = in_file.readline()
            while line:
                while line.count('"') % 2:
                    line = line.rstrip('\n')
                    line += in_file.readline()
                out_file.write(line)
                line = in_file.readline()
    if modified:
        copyfile(out_file_path, in_file_path)
    os.remove(out_file_path)

def translate_csv_file(in_file_path, out_file_path, table_name):
    with open(out_file_path, 'w', encoding="utf-8-sig") as out_file:
        with open(in_file_path, 'r', encoding="utf-8-sig") as in_file:
            column_raw_names = in_file.readline().rstrip('\n').split(",")
            column_count = len(column_raw_names)

            column_names = in_file.readline().rstrip('\n')\
                .replace('{', '').replace('}', '')\
                .replace('[', '').replace(']', '')\
                .replace('(', '').replace(')', '')\
                .replace('<', '').replace('>', '')\
                .replace('/', '').replace('\\', '')\
                .replace('\'', '').replace('\"', '')\
                .replace(' ', '_').replace('*', '')\
                .replace('%', 'pct').replace('$', 'sss').split(",")

            column_types = in_file.readline().rstrip('\n').split(",")

            header_names = ""
            header_vars = ""
            header_stringify_vars = ""
            stringify_vars = ""

            for column_name, column_raw_name in zip(column_names, column_raw_names):
                header_names += "            , \"{0}\"\n".format(column_raw_name)
                header_vars += "                {0} out_entry.{1}_\n".format( "," if len(header_vars) > 0 else " ", "id" if len(header_vars) == 0 else (column_name if len(column_name) > 0 else "c{0}".format(column_raw_name)))
                header_stringify_vars += "                {0} \"{1}\"\n".format("," if len(header_stringify_vars) > 0 else " ", "id" if len(header_vars) == 0 else (column_name if len(column_name) > 0 else "c{0}".format(column_raw_name)))

            variable_defs = ""
            using_defs = ""
            stringify_string = ""
            seen_types = set()
            for column_type, column_name, column_raw_name in zip(column_types, column_names, column_raw_names):
                cname_pre = "id" if len(variable_defs) == 0 else (column_name if len(column_name) > 0 else "c{0}".format(column_raw_name))
                cname = "out_entry.{0}".format(cname_pre)

                if column_type == "str":
                    column_type = "std::string"
                    stringify_string = "{0}_".format(cname)
                elif column_type == "int64":
                    column_type = "StringInt64"
                    stringify_string = "{0}_".format(cname)
                elif column_type == "uint64":
                    column_type = "StringInt64"
                    stringify_string = "{0}_".format(cname)
                elif column_type == "int32":
                    column_type = "int32_t"
                    stringify_string = "std::to_string({0}_)".format(cname)
                elif column_type == "uint32":
                    column_type = "uint32_t"
                    stringify_string = "std::to_string({0}_)".format(cname)
                elif column_type == "int16":
                    column_type = "int16_t"
                    stringify_string = "std::to_string({0}_)".format(cname)
                elif column_type == "uint16":
                    column_type = "uint16_t"
                    stringify_string = "std::to_string({0}_)".format(cname)
                elif column_type == "byte":
                    column_type = "uint8_t"
                    stringify_string = "std::to_string(static_cast<uint32_t>({0}_))".format(cname)
                elif column_type == "sbyte":
                    column_type = "int8_t"
                    stringify_string = "std::to_string(static_cast<int32_t>({0}_))".format(cname)
                elif column_type == "single":
                    column_type = "float"
                    stringify_string = "std::to_string({0}_)".format(cname)
                elif column_type.startswith("bit"):
                    column_type = "StringBool"
                    stringify_string = "{0}_".format(cname)
                elif column_type.startswith("bool"):
                    column_type = "StringBool"
                    stringify_string = "{0}_".format(cname)
                elif column_type not in seen_types:
                    seen_types.add(column_type)
                    using_defs += "    using {0} = int32_t;\n".format(column_type)
                    stringify_string = "std::to_string({0}_)".format(cname)
                variable_defs += "    {0} {1}_;\n".format(column_type, cname_pre)
                stringify_vars += "                    {0} {1}\n".format("," if len(stringify_vars) > 0 else " ", stringify_string)

        with open("./cpp-record-class-template.h", 'r', encoding="utf-8-sig") as in_file:
            data = in_file.read()
            data = data.format(table_name, column_count, using_defs, stringify_vars, variable_defs, header_names, header_vars, header_stringify_vars)
            out_file.write(data)

def generate_all_tables_header(file_names, table_names):
    include_lines = ""
    table_enum_lines = ""
    csv_entry_lines = ""
    load_table_lines = ""
    index = 0
    for file_name, table_name in zip(file_names, table_names):
        include_lines += "#include \"tables/{0}\"\n".format(file_name)
        csv_entry_lines += "    {0} \"{1}\"\n".format(" " if len(csv_entry_lines) == 0 else ",", table_name)
        table_enum_lines += "    {0} {1}\n".format(" " if len(table_enum_lines) == 0 else ",", table_name)
        load_table_lines += "CsvTable<{0}TableEntry> g_{1};\n".format(table_name, file_name.replace("/", "_").replace(".h", ""))
        load_table_lines += "void Load{0}Table() {{ g_{1}.LoadCsv(g_csv_path + g_table_csv_names[{2}] + g_csv_suffix); }}\n\n".format(table_name, file_name.replace("/", "_").replace(".h", ""), index)
        index += 1

    with open("./cpp-all-tables-template.h", 'r', encoding="utf-8-sig") as in_file:
        data = in_file.read()
        data = data.format(include_lines, table_enum_lines, index, csv_entry_lines, load_table_lines)
        with open("all_tables.h", 'w', encoding="utf-8-sig") as out_file:
            out_file.write(data)

def to_snake_case(in_str):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', in_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def csv_ignore_list():
    ignore_list = list()
    ignore_list.append("CharaMakeType.csv")
    ignore_list.append("HairMakeType.csv")
    ignore_list.append("Quest.csv")
    ignore_list.append("SpecialShop.csv")
    ignore_list.append("Story.csv")
    ignore_list.append("GuildOrderGuide.csv")
    ignore_list.append("GuildOrderOfficer.csv")
    ignore_list.append("GuildleveAssignment.csv")
    ignore_list.append("Aetheryte.csv")
    ignore_list.append("ChocoboTaxiStand.csv")
    ignore_list.append("quest.*")
    return ignore_list

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: {0} csv_dir out_dir".format(sys.argv[0]))
        sys.exit()

    csv_dir = sys.argv[1]
    out_dir = sys.argv[2]

    file_names = list()
    table_names = list()

    ignore_list = csv_ignore_list()

    files_processed = 0
    for dirpath, dirs, files in os.walk(csv_dir):
        for filename in files:
            files_processed += 1
            if files_processed % 10 == 0:
                print("Files processed: {0}".format(files_processed))
            skip_file = False
            for ignore_expr in ignore_list:
                if re.match(ignore_expr, filename):
                    skip_file = True
                    break
            if skip_file:
                continue
            in_filename = os.path.join(dirpath, filename).replace("\\", "/")
            if in_filename.endswith(".csv"):
                dir_segment_list = dirpath.split('\\')
                dirpath_string = os.path.join(*(dir_segment_list[1:])).replace("\\", "/") if len(dir_segment_list) > 1 else ""
                out_filename = os.path.join(out_dir, dirpath_string, to_snake_case(filename.replace(".csv", "_table.h"))).replace("\\", "/")
                file_names.append(os.path.join(*(out_filename.split("/")[1:])).replace("\\", "/"))
                out_tablename = filename.replace(".csv", "")
                table_names.append(out_tablename)

                if os.path.exists(out_filename):
                    continue
                if not os.path.exists(os.path.dirname(out_filename)):
                    os.makedirs(os.path.dirname(out_filename))
                fixup_csv_file(in_filename)
                translate_csv_file(in_filename, out_filename, out_tablename)

    # generate_all_tables_header(file_names, table_names)
