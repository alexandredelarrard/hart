from itertools import islice


def batched(iterable, n):
    # this is shipped within iterools wiht python >= 3.12
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def batched_with_overlap(iterable, n, overlap):
    """TODO: Delete"""
    if n <= overlap:
        raise ValueError("Batch size must be larger than overlap")
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    prev_batch = tuple(islice(it, n))
    if prev_batch:
        yield prev_batch
    while prev_batch:
        skipped = prev_batch[n - overlap :]
        batch = tuple(skipped + tuple(islice(it, n - overlap)))
        if len(batch) == n:
            yield batch
        prev_batch = batch


def fixed_size_chunking_with_overlap(tokens, chunk_size, chunk_overlap):
    if chunk_overlap > chunk_size:
        raise ValueError(
            f"chunk_size > chunk_overlap, got {(chunk_size, chunk_overlap) = }"
        )

    chunks = []
    start_idx = 0
    while start_idx < len(tokens):
        chunk = tokens[start_idx : start_idx + chunk_size]
        chunks.append(chunk)
        start_idx += chunk_size - chunk_overlap

    return chunks


def split_text_into_chunks(
    text: str,
    chunk_size=512,
    chunk_overlap=0,
    tokenize=None,
    untokenize=None,
):
    tokens = tokenize(text)

    chunks = fixed_size_chunking_with_overlap(tokens, chunk_size, chunk_overlap)

    chunks = [untokenize(chunk).strip() for chunk in chunks]

    # remove last chunk if it doesn't contain any new information
    if len(chunks[-1]) <= chunk_overlap:
        del chunks[-1]

    return chunks
