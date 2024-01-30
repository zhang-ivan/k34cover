# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import galois


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    f = galois.GF(4, repr="power")
    print(f.arithmetic_table("+"))
    a = f.primitive_element
    i = a**0
    print(i)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
