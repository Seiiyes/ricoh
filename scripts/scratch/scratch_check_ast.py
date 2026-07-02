import ast

class SessionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.function_decorators = {}
        self.function_accesses_session = set()
        
    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        
        # Store decorators
        decs = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decs.append(dec.id)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
                decs.append(dec.func.id)
        self.function_decorators[node.name] = decs
        
        self.generic_visit(node)
        self.current_function = old_function
        
    def visit_Attribute(self, node):
        if node.attr == 'session' and isinstance(node.value, ast.Name) and node.value.id == 'self':
            if self.current_function:
                self.function_accesses_session.add(self.current_function)
        self.generic_visit(node)

with open('backend/services/ricoh_web_client.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())

visitor = SessionVisitor()
visitor.visit(tree)

print(f"{'Función':<40} | {'Decoradores':<35} | {'Tiene with_printer_session?':<30}")
print("-" * 115)
for func in sorted(visitor.function_accesses_session):
    decs = visitor.function_decorators.get(func, [])
    has_dec = "Sí" if "with_printer_session" in decs else "NO ❌"
    print(f"{func:<40} | {str(decs):<35} | {has_dec:<30}")
