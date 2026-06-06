"""String Algorithms 4: Trie (Prefix Tree)"""


class TrieNode:
    """A node in a trie (prefix tree)."""
    def __init__(self):
        self.children: dict = {}
        self.is_end: bool = False
        self.count: int = 0  # number of words ending here


class Trie:
    """Trie data structure for efficient prefix-based string operations."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.count += 1

    def search(self, word: str) -> bool:
        """Return True if the exact word is in the trie."""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word in the trie starts with the given prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

    def count_prefix(self, prefix: str) -> int:
        """Count how many words in the trie start with the given prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return 0
            node = node.children[ch]
        return self._count_words(node)

    def _count_words(self, node: TrieNode) -> int:
        """Recursively count words in the subtree rooted at node."""
        total = node.count
        for child in node.children.values():
            total += self._count_words(child)
        return total

    def autocomplete(self, prefix: str, limit: int = 10) -> list:
        """Return up to `limit` words that start with the given prefix."""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        results: list = []
        self._collect(node, prefix, results, limit)
        return results

    def _collect(self, node: TrieNode, path: str,
                 results: list, limit: int) -> None:
        """DFS to collect words from the trie."""
        if len(results) >= limit:
            return
        if node.is_end:
            results.append(path)
        for ch in sorted(node.children.keys()):
            self._collect(node.children[ch], path + ch, results, limit)


def longest_common_prefix(words: list) -> str:
    """Find the longest common prefix among a list of strings
    using a character-by-character comparison."""
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        i = 0
        while i < len(prefix) and i < len(word) and prefix[i] == word[i]:
            i += 1
        prefix = prefix[:i]
        if not prefix:
            return ""
    return prefix


if __name__ == "__main__":
    trie = Trie()
    for w in ["apple", "app", "apricot", "banana", "band", "ban"]:
        trie.insert(w)

    assert trie.search("app") is True
    assert trie.search("ap") is False
    assert trie.starts_with("ap") is True
    assert trie.starts_with("bx") is False
    assert trie.count_prefix("ap") == 3
    assert trie.count_prefix("ban") == 3
    assert trie.autocomplete("ap") == ["app", "apple", "apricot"]

    assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_common_prefix(["abc"]) == "abc"
    assert longest_common_prefix([]) == ""
    print("All trie tests passed.")
