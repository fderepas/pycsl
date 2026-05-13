def normalize(text):
    letters = []
    for ch in text.lower():
        if ch.isalnum():
            letters.append(ch)
    return "".join(letters)


def is_palindrome(text):
    cleaned = normalize(text)
    return cleaned == cleaned[::-1]


def word_count(text):
    tokens = [part for part in text.strip().split() if part]
    return len(tokens)


if __name__ == "__main__":
    sample = "A man, a plan, a canal: Panama!"
    print("palindrome:", is_palindrome(sample))
    print("word_count:", word_count("one two   three"))

