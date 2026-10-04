"""
EldenLang Lexer
Tokenizes .el source files into a flat list of Token objects.
"""

from dataclasses import dataclass
from typing import List


# ── Token types ────────────────────────────────────────────────────────────────

KEYWORDS = {
    # Program structure
    "SEEK", "GRACE", "OFFER", "REMEMBRANCE",
    # Variables
    "INSCRIBE", "SHATTER",
    # Arithmetic (standalone statements)
    "KINDLE", "WANE", "FORGE", "CLEAVE", "MODULO",
    # I/O
    "ECHO", "HEAR",
    # Conditionals
    "FOG", "GATE", "MIST", "LIFT", "FOG",
    # Loops
    "ERDTREE", "LOOP", "ROOTS", "END", "FELL", "THE", "TREE",
    # Functions
    "INCANTATION", "CAST", "BESTOWED",
    # Conditions
    "IS", "NOT", "EXCEEDS", "YIELDS", "TO",
    # Save/Restore (bonus feature)
    # "REMEMBER", "RECALL",
    # Return value inside incantation
    "RETURN",
}

# Multi-word compound keywords (longest match first)
COMPOUND_KEYWORDS = [
    "SEEK GRACE",
    "OFFER REMEMBRANCE",
    "FOG GATE",
    "LIFT FOG",
    "ERDTREE LOOP",
    "ROOTS END",
    "FELL THE TREE",
    "GRACE BESTOWED",
    "IS NOT",
    "YIELDS TO",
]

TK_KEYWORD   = "KEYWORD"
TK_IDENT     = "IDENT"
TK_NUMBER    = "NUMBER"
TK_STRING    = "STRING"
TK_BOOL      = "BOOL"
TK_NULL      = "NULL"
TK_NEWLINE   = "NEWLINE"
TK_EOF       = "EOF"


@dataclass
class Token:
    type: str
    value: object
    line: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


# ── Lexer ──────────────────────────────────────────────────────────────────────

class LexError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        for lineno, raw_line in enumerate(self.lines, start=1):
            line = raw_line.strip()


            if not line or line.startswith("~"):
                continue


            line = self._strip_comment(line)

            self._tokenize_line(line, lineno)

        self.tokens.append(Token(TK_EOF, None, len(self.lines)))
        return self.tokens

    def _strip_comment(self, line: str) -> str:

        in_string = False
        for i, ch in enumerate(line):
            if ch == '"':
                in_string = not in_string
            if not in_string and ch == '~' and i > 0 and line[i-1] == ' ':
                return line[:i].strip()
        return line

    def _tokenize_line(self, line: str, lineno: int):

        upper = line.upper()

        for ck in COMPOUND_KEYWORDS:
            if upper.startswith(ck):
                self.tokens.append(Token(TK_KEYWORD, ck, lineno))
                rest = line[len(ck):].strip()
                if rest:
                    self._tokenize_args(rest, lineno)
                return


        parts = line.split()
        i = 0
        while i < len(parts):
            word = parts[i]
            upper_word = word.upper()

            # Booleans
            if upper_word == "GRACE":
                self.tokens.append(Token(TK_BOOL, True, lineno))
                i += 1
                continue
            if upper_word == "LOST":
                self.tokens.append(Token(TK_BOOL, False, lineno))
                i += 1
                continue
            if upper_word == "VOID":
                self.tokens.append(Token(TK_NULL, None, lineno))
                i += 1
                continue

            # Compound conditions (IS NOT, YIELDS TO)
            if upper_word == "IS" and i + 1 < len(parts) and parts[i+1].upper() == "NOT":
                self.tokens.append(Token(TK_KEYWORD, "IS NOT", lineno))
                i += 2
                continue
            if upper_word == "YIELDS" and i + 1 < len(parts) and parts[i+1].upper() == "TO":
                self.tokens.append(Token(TK_KEYWORD, "YIELDS TO", lineno))
                i += 2
                continue

            # Keywords
            if upper_word in KEYWORDS:
                self.tokens.append(Token(TK_KEYWORD, upper_word, lineno))
                i += 1
                continue

            # Numbers
            try:
                num = float(word) if "." in word else int(word)
                self.tokens.append(Token(TK_NUMBER, num, lineno))
                i += 1
                continue
            except ValueError:
                pass

            # Strings
            if word.startswith('"'):
                joined = " ".join(parts[i:])
                end = joined.find('"', 1)
                if end == -1:
                    raise LexError(f"Line {lineno}: unterminated string")
                string_val = joined[1:end]
                self.tokens.append(Token(TK_STRING, string_val, lineno))
                consumed = joined[:end+1]
                count = consumed.count(" ") - (len(consumed) - len(consumed.lstrip())) + 1
                i += len(consumed.split())
                continue

            # Identifiers (variable/function names)
            if word.isidentifier():
                self.tokens.append(Token(TK_IDENT, word, lineno))
                i += 1
                continue

            raise LexError(f"Line {lineno}: unexpected token '{word}'")

    def _tokenize_args(self, rest: str, lineno: int):
        self._tokenize_line(rest, lineno)