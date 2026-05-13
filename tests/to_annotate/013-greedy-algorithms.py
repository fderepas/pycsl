def select_max_non_overlapping(intervals):
    sorted_intervals = sorted(intervals, key=lambda x: x[1])
    selected = []
    last_end = None
    for start, end in sorted_intervals:
        if start > end:
            raise ValueError("interval start must be <= end")
        if last_end is None or start >= last_end:
            selected.append((start, end))
            last_end = end
    return selected


if __name__ == "__main__":
    data = [(1, 3), (2, 5), (4, 7), (1, 8), (8, 9), (5, 9)]
    print("selected:", select_max_non_overlapping(data))

