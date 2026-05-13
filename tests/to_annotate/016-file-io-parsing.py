import csv


def read_scores_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"name", "score"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must contain name and score columns")
        for row in reader:
            name = row["name"].strip()
            score = int(row["score"])
            rows.append((name, score))
    return rows


def average_score(entries):
    if not entries:
        return 0.0
    total = sum(score for _, score in entries)
    return total / len(entries)


if __name__ == "__main__":
    path = "sample_scores.csv"
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write("name,score\nAlice,10\nBob,14\n")
    parsed = read_scores_csv(path)
    print("rows:", parsed)
    print("average:", average_score(parsed))

