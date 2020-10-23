import operator


def main():
    dct = {"boi": {"name": "headass", "age" : 69}, "grill": {
        "name:": "asshead", "age": 96}}
    dct_2 = sorted(dct.items(), key=lambda x: x[1]["age"], reverse=True)
    print(dct_2)


if __name__ == "__main__":
    main()