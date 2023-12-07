def create_large_list(size):
    large_list = bytearray()
    for i in range(size):
        large_list.extend(b" " * (1024 * 1024))  # Appending 1 MB of empty bytes to the bytearray
    return large_list
# Creating a bytearray with 10,000 empty bytes, each of size 1 MB
my_large_list = create_large_list(10000)
# Optimizing memory usage by utilizing a bytearray instead of a list of strings