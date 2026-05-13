def first_duplicate(values):
    seen = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def group_anagrams(words):
    groups = {}
    for word in words:
        key = "".join(sorted(word))
        groups.setdefault(key, []).append(word)
    return list(groups.values())


if __name__ == "__main__":
    print("first duplicate:", first_duplicate([3, 1, 4, 2, 4, 5]))
    print("anagrams:", group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))

