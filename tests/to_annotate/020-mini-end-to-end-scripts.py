import argparse


def count_non_empty_lines(path):
    count = 0
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Count non-empty lines in a text file.")
    parser.add_argument("path", help="Path to a text file")
    args = parser.parse_args()
    print(count_non_empty_lines(args.path))


if __name__ == "__main__":
    main()
