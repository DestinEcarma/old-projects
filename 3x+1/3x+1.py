from matplotlib import pyplot as plt

def main():
    v = int(input("Enter a number: "))
    x = []
    y = []

    def even(v):
        v = v * 3 + 1
        y.append(v)
        return v

    def odd(v):
        v = v / 2
        y.append(v)
        return v


    if v:
        x.append(1)
        y.append(v)
        counter = 1

        while v != 1:
            if (v % 2) == 0:
                v = odd(v)
            else:
                v = even(v)

            counter += 1
            x.append(counter)

    plt.plot(x, y)
    plt.show()

if __name__ == "__main__":
    main()