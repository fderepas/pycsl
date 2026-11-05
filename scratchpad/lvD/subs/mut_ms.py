SUBS=[('''        if name is None:
            name = "_"
        self.write(f"*{name}")''','''        if name is None:
            name = "_"
        self._indent = 7
        self.write(f"*{name}")''')]
