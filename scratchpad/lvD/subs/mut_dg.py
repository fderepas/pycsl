SUBS=[('''        for label, ok in self.pairwise.items():
            lines.append(f"  {label}: {'PASS' if ok else 'FAIL'}")
        return "\\n".join(lines)''','''        for label, ok in self.pairwise.items():
            lines.append(f"  {label}: {'PASS' if ok else 'FAIL'}")
        self.qualname = "mutated"
        return "\\n".join(lines)''')]
