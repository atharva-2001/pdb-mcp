def greet(name):
    greeting = f"Hello, {name}!"
    return greeting


def main():
    names = ["Alice", "Bob", "Charlie"]
    for name in names:
        result = greet(name)
        print(result)


if __name__ == "__main__":
    main()
