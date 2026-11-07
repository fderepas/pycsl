SUBS=[('        if name is None:\n            name = "_"\n        self.write(f"*{name}")', '        if name is None:\n            name = node.name\n        self.write(f"*{name}")')]
