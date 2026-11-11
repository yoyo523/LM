"""Parse a .kln file and print its AST as JSON; this does not execute it."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from .lexer_adapter import tokenize
from .parser import Parser


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('source', type=Path)
    args = cli.parse_args()
    try:
        source = args.source.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        print(f'{args.source}: {error}', file=sys.stderr)
        return 1
    tokens, errors = tokenize(source)
    result = Parser(tokens).parse()
    errors.extend(result.diagnostics)
    if errors:
        for error in sorted(errors, key=lambda e: (e.line, e.column)):
            print(f'{args.source}:{error.line}:{error.column}: {error.message}', file=sys.stderr)
        return 1
    print(json.dumps(asdict(result.program), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
