def word_frequencies(words):
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def unique_sorted_values(values):
    return sorted(set(values))


def index_by_id(rows):
    indexed = {}
    for row in rows:
        key = row["id"]
        indexed[key] = row
    return indexed


if __name__ == "__main__":
    words = ["red", "blue", "red", "green", "blue", "red"]
    rows = [{"id": 10, "name": "Ada"}, {"id": 20, "name": "Linus"}]
    print("freq:", word_frequencies(words))
    print("unique:", unique_sorted_values([3, 3, 1, 2, 1]))
    print("index:", index_by_id(rows))

