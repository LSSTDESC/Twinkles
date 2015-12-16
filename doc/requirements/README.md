# Twinkles Requirements Documents

Currently just Twinkles 1. Parts of this will be included into
a DC1 requirements document, assembled by the SSim working group. As a
result, of this, and in  anticipation of Twinkles 2,
the  Twinkles 1 source files are stored
in their own sub-directory, and compiled into a master document
called `TwinklesRQ.tex`.

### Compiling

Compile from the `doc/requirements` directory.

The documents use the Science Roadmap macros and settings. To link the
required files to this directory, do (in csh):
```
setenv SRM_DIR <path_to_Science_Roadmap_repo>
make links
```
or in [ba]sh
```
export SRM_DIR=<path_to_Science_Roadmap_repo>
make links
```

Then, compile with `make`.
