"""
EldenLang Parser
Consumes a flat token list and produces an AST (list of statement nodes).

"""

from typing import List, Any
from lexer import Token, TK_KEYWORD, TK_IDENT, TK_NUMBER, TK_STRING, TK_BOOL, TK_NULL, TK_EOF


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ── Helpers ────────────────────────────────────────────────────────────────

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect_keyword(self, value: str) -> Token:
        tok = self.advance()
        if tok.type != TK_KEYWORD or tok.value != value:
            raise ParseError(
                f"Line {tok.line}: expected keyword '{value}', got {tok.type}:{tok.value!r}"
            )
        return tok

    def expect_ident(self) -> Token:
        tok = self.advance()
        if tok.type != TK_IDENT:
            raise ParseError(f"Line {tok.line}: expected identifier, got {tok.type}:{tok.value!r}")
        return tok

    def at_keyword(self, value: str) -> bool:
        tok = self.peek()
        return tok.type == TK_KEYWORD and tok.value == value

    def at_eof(self) -> bool:
        return self.peek().type == TK_EOF

    # ── Value expression ───────────────────────────────────────────────────────

    def parse_value(self) -> dict:
        """Parse a literal or identifier."""
        tok = self.advance()
        if tok.type == TK_NUMBER:
            return {"kind": "literal", "value": tok.value}
        if tok.type == TK_STRING:
            return {"kind": "literal", "value": tok.value}
        if tok.type == TK_BOOL:
            return {"kind": "literal", "value": tok.value}
        if tok.type == TK_NULL:
            return {"kind": "literal", "value": None}
        if tok.type == TK_IDENT:
            return {"kind": "var", "name": tok.value}
        raise ParseError(f"Line {tok.line}: expected a value, got {tok.type}:{tok.value!r}")

    # ── Condition ──────────────────────────────────────────────────────────────

    def parse_condition(self) -> dict:
        """Parse: <val> <op> <val>"""
        left = self.parse_value()
        op_tok = self.advance()
        if op_tok.type != TK_KEYWORD or op_tok.value not in ("IS", "IS NOT", "EXCEEDS", "YIELDS TO"):
            raise ParseError(
                f"Line {op_tok.line}: expected condition operator, got {op_tok.value!r}"
            )
        op = op_tok.value
        right = self.parse_value()
        return {"kind": "condition", "left": left, "op": op, "right": right}

    # ── Statement list ─────────────────────────────────────────────────────────

    def parse_body(self, stop_keywords: List[str]) -> List[dict]:
        """Parse statements until one of stop_keywords appears."""
        stmts = []
        while not self.at_eof():
            if self.peek().type == TK_KEYWORD and self.peek().value in stop_keywords:
                break
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self) -> dict:
        tok = self.peek()
        if tok.type != TK_KEYWORD:
            raise ParseError(f"Line {tok.line}: statement must begin with a keyword, got {tok.type}:{tok.value!r}")

        kw = tok.value

        # ── INSCRIBE <name> <value> ──
        if kw == "INSCRIBE":
            self.advance()
            name = self.expect_ident().value
            val = self.parse_value()
            return {"kind": "inscribe", "name": name, "value": val}

        # ── SHATTER <name> ──
        if kw == "SHATTER":
            self.advance()
            name = self.expect_ident().value
            return {"kind": "shatter", "name": name}

        # ── KINDLE/WANE/FORGE/CLEAVE/MODULO <name> <value> ──
        if kw in ("KINDLE", "WANE", "FORGE", "CLEAVE", "MODULO"):
            self.advance()
            name = self.expect_ident().value
            val = self.parse_value()
            return {"kind": "arith", "op": kw, "name": name, "value": val}

        # ── ECHO <value> ──
        if kw == "ECHO":
            self.advance()
            val = self.parse_value()
            return {"kind": "echo", "value": val}

        # ── HEAR <name> ──
        if kw == "HEAR":
            self.advance()
            name = self.expect_ident().value
            return {"kind": "hear", "name": name}

        # ── FOG GATE <cond> … MIST … LIFT FOG ──
        if kw == "FOG GATE":
            self.advance()
            cond = self.parse_condition()
            then_body = self.parse_body(["MIST", "LIFT FOG"])
            else_body = []
            if self.at_keyword("MIST"):
                self.advance()
                else_body = self.parse_body(["LIFT FOG"])
            self.expect_keyword("LIFT FOG")
            return {"kind": "fog_gate", "cond": cond, "then": then_body, "else": else_body}

        # ── ERDTREE LOOP … ROOTS END ──
        if kw == "ERDTREE LOOP":
            self.advance()
            body = self.parse_body(["ROOTS END"])
            self.expect_keyword("ROOTS END")
            return {"kind": "erdtree_loop", "body": body}

        # ── FELL THE TREE ──
        if kw == "FELL THE TREE":
            self.advance()
            return {"kind": "fell_tree"}

        # ── INCANTATION <name> … GRACE BESTOWED ──
        if kw == "INCANTATION":
            self.advance()
            name = self.expect_ident().value

            params = []
            while self.peek().type == TK_IDENT:
                params.append(self.advance().value)
            body = self.parse_body(["GRACE BESTOWED"])
            self.expect_keyword("GRACE BESTOWED")
            return {"kind": "incantation", "name": name, "params": params, "body": body}

        # ── CAST <name> [args...] ──
        if kw == "CAST":
            self.advance()
            name = self.expect_ident().value
            args = []
            while not self.at_eof() and self.peek().type in (
                TK_IDENT, TK_NUMBER, TK_STRING, TK_BOOL, TK_NULL
            ):
                args.append(self.parse_value())
            return {"kind": "cast", "name": name, "args": args, "target": None}

        # ── OFFER REMEMBRANCE [value] ──
        if kw == "OFFER REMEMBRANCE":
            self.advance()
            val = None
            if not self.at_eof() and self.peek().type in (
                TK_IDENT, TK_NUMBER, TK_STRING, TK_BOOL, TK_NULL
            ):
                val = self.parse_value()
            return {"kind": "offer_remembrance", "value": val}

        # ── RETURN <value> (inside incantation) ──
        if kw == "RETURN":
            self.advance()
            val = self.parse_value()
            return {"kind": "return", "value": val}

        # ── REMEMBER <slot> ──
        """
        if kw == "REMEMBER":
            self.advance()
            slot = self.expect_ident().value
            return {"kind": "remember", "slot": slot}

        # ── RECALL <slot> ──
        if kw == "RECALL":
            self.advance()
            slot = self.expect_ident().value
            return {"kind": "recall", "slot": slot}

        raise ParseError(f"Line {tok.line}: unknown statement keyword '{kw}'")
        """

    # ── Top-level ──────────────────────────────────────────────────────────────

    def parse(self) -> List[dict]:
        """Parse the whole program: [INCANTATION defs] SEEK GRACE … OFFER REMEMBRANCE"""
        # Collect top-level incantation definitions before SEEK GRACE
        top_level = []
        while not self.at_eof() and self.at_keyword("INCANTATION"):
            top_level.append(self.parse_statement())

        self.expect_keyword("SEEK GRACE")
        body = self.parse_body(["OFFER REMEMBRANCE"])
        self.expect_keyword("OFFER REMEMBRANCE")
        return top_level + body