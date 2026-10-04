class FellTreeException(Exception):
    pass

class OfferRemembrance(Exception):
    def __init__(self, value=None):
        self.value = value

class RuntimeError_(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.env = {}  # Variables storage
        self.incantations = {} # Function definitions
        self.last_cast_result = None

    def evaluate(self, node):
        kind = node.get("kind")

        if kind == "inscribe":
            self.env[node["name"]] = self.evaluate(node["value"])

        elif kind == "shatter":
            del self.env[node["name"]]

        elif kind == "arith":
            val = self.evaluate(node["value"])
            curr = self.env.get(node["name"], 0)
            if node["op"] == "KINDLE":
                self.env[node["name"]] = curr + val
            elif node["op"] == "WANE":
                self.env[node["name"]] = curr - val
            elif node["op"] == "FORGE":
                self.env[node["name"]] = curr * val
            elif node["op"] == "CLEAVE":
                self.env[node["name"]] = curr / val
            elif node["op"] == "MODULO":
                self.env[node["name"]] = curr % val

        elif kind == "echo":
            print(self.evaluate(node["value"]))

        elif kind == "literal":
            return node["value"]

        elif kind == "var":
            return self.env.get(node["name"])

        elif kind == "fell_tree":
            raise FellTreeException

        elif kind == "hear":
            raw = input()
            try:
                self.env[node["name"]] = int(raw)
            except ValueError:
                try:
                    self.env[node["name"]] = float(raw)
                except ValueError:
                    self.env[node["name"]] = raw

        elif kind == "fog_gate":
            if self.check_condition(node["cond"]):
                for stmt in node["then"]:
                    self.evaluate(stmt)
            else:
                for stmt in node["else"]:
                    self.evaluate(stmt)

        elif kind == "erdtree_loop":
            try:
                while True:
                    self.run(node["body"])
            except FellTreeException:
                return None

        elif kind == "incantation":
            self.incantations[node["name"]] = node

        elif kind == "cast":
            result = self._call_incantation(node["name"], node["args"], self.env)
            self.last_cast_result = result

            self.env["_result"] = result
            if node.get("target"):
                self.env[node["target"]] = result

        elif kind == "offer_remembrance":
            val = self._eval(node["value"], self.env) if node["value"] else None
            raise OfferRemembrance(val)

        elif kind == "return":
            val = self._eval(node["value"], self.env)
            raise OfferRemembrance(val)

        return None

    def _eval(self, node: dict, env: dict):
        if node is None:
            return None
        kind = node["kind"]
        if kind == "literal":
            return node["value"]
        if kind == "var":
            return env.get(node["name"])
        raise RuntimeError_(f"Cannot evaluate node of kind '{kind}'")

    def _call_incantation(self, name: str, arg_nodes: list, caller_env: dict):
        if name not in self.incantations:
            raise RuntimeError_(f"Incantation '{name}' has not been defined.")

        fn = self.incantations[name]
        params = fn["params"]
        args = [self._eval(a, caller_env) for a in arg_nodes]

        if len(args) != len(params):
            raise RuntimeError_(
                f"Incantation '{name}' expects {len(params)} runes, "
                f"but {len(args)} were offered."
            )

        fn_env = self.env
        for p, a in zip(params, args):
            fn_env[p] = a

        try:
            self.run(fn["body"])
            self.run(fn_env)
            return None
        except OfferRemembrance as r:
            return r.value

    def run(self, ast):
        for stmt in ast:
            self.evaluate(stmt)

    def check_condition(self, cond):
        left = self.evaluate(cond["left"])
        right = self.evaluate(cond["right"])
        op = cond.get("op")

        if op == "IS NOT": return left != right
        elif op == "IS": return left == right
        elif op == "EXCEEDS": return left > right
        elif op == "YIELDS TO": return left < right
        return False

