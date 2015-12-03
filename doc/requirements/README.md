# Twinkles Requirements Documents

Currently just Twinkles 1. This will form part of a larger DC1
requirements document, assembled by the SSim working group. As a
result, and in  anticipation, the  Twinkles 1 source files are stored
in their own sub-directory, and compiled into a dummy master document
called `dc1.tex`.

### Compiling

The documents use the Science Roadmap macros and settings. To link the
required files to this directory, do
```
setenv SRM_DIR <path_to_Science_Roadmap_repo>
make links
```
Then, compile `dc1.pdf` with `make`.
