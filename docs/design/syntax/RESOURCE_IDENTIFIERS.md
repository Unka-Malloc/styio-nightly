# Resource Identifiers

**Purpose:** Define the current implemented Styio resource identifier surface as compact built-in symbolic definitions.

**Last updated:** 2026-04-23

These are compiler built-ins, not user-authored wrapper declarations.

```styio
@stdin  := { << ( >_ ) }
@stdout := { x -> ( >_ ) }
@stderr := { !(x) -> ( >_ ) }

@file{path} := { file(path) }
@{path}     := @file{path}

@stdin: list[T] := { read_as<list[T]>(@stdin) }
```

| Identifier | Direction |
|------------|-----------|
| `@stdin` | read |
| `@stdout` | write |
| `@stderr` | write |
| `@file{path}` | read/write |
| `@{path}` | read/write |
| `@stdin: list[T]` | read |

Target-only driver identifiers such as `@mysql{...}`, `@http{...}`, and `@kafka{...}` are not part of this current surface.
