project 'ffxiv-datamining'
    kind 'Utility'
    language 'C++'
    cppdialect 'C++14'

    targetdir 'bin/%{cfg.buildcfg}'

    postbuildcommands
    {
        '{COPY} csv "bin/%{cfg.buildcfg}/csv"'
    }
