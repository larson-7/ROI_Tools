
def fib(n, sequence = [1]):
    if n == 0:
        return sequence
    else:
        n -= 1
        sequence.append(sum(sequence[-2:]))
        return fib(n, sequence)


print(fib(10))