import re


def is_palindrome(text: str) -> bool:
    cleaned = text.replace(" ", "").lower()
    return cleaned == cleaned[::-1]


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n musi być liczbą nieujemną")
    
    if n == 0:
        return 0
    if n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    vowels = "aeiouyąęó"
    return sum(1 for char in text.lower() if char in vowels)


def calculate_discount(price: float, discount: float) -> float:
    if discount < 0 or discount > 1:
        raise ValueError("Zniżka musi być w zakresie 0-1")
    
    return price * (1 - discount)


def flatten_list(nested_list: list) -> list:
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def word_frequencies(text: str) -> dict:
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    
    words = cleaned.split()
    
    frequencies = {}
    for word in words:
        if word:
            frequencies[word] = frequencies.get(word, 0) + 1
    
    return frequencies


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    
    if n == 2:
        return True
    
    if n % 2 == 0:
        return False

    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    
    return True

