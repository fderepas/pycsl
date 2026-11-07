SUBS=[('''        if name is None:
            name = "_"
        self.write(f"*{name}")''','''        if name is None:
            name = ["_"]
        self.write(f"*{name}")''')]
