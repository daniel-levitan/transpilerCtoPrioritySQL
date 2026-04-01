# STC Transpiler

A transpiler from a custom C-like language to **Priority SQL** — the procedural
SQL dialect used by [Priority Software](https://prioritysoftware.github.io/sdk/Flow-Control).

Built from scratch: hand-written lexer, recursive descent parser, AST, and code generator.

## Pipeline
```
source.stc → Lexer → Tokens → Parser → AST → CodeGenerator → Priority SQL
```

## What it transpiles

Variable declarations (`int`, `real`, `char`, `date`, `day`, `time`), assignment,
arithmetic and logical expressions, `if/else`, `while`, `print`, `select`, and
`foreach` — a cursor loop that wraps a `SELECT` and iterates over its result set.

**Source:**
```c
int x = 5;
if (x > 0) {
    print(x);
} else {
    x = 0;
}
```

**Output:**
```sql
:x = 5;
GOTO 1 WHERE NOT (x > 0);
SELECT :x FROM DUMMY ASCII;
GOTO 2;
LABEL 1;
:x = 0;
LABEL 2;
```

## Implementation notes

Operator context is tracked through code generation — the same `==` emits `=`
in a condition and `(a = b ? 1 : 0)` in a value context, matching Priority SQL's
lack of a boolean type. Variables are prefixed with `:` in value context and left
bare in conditions, following Priority's convention.

`foreach` compiles to a full cursor block: `DECLARE`, `OPEN`, `FETCH` loop with
`GOTO`-based error handling, and `CLOSE` — all label indices managed by a counter
in the code generator.

## Usage
```bash
python3 main.py <file.stc>
```

Requires Python 3.10+ (uses `match` in the lexer). No external dependencies.