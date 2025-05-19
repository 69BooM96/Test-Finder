import json

def chunk_list(lst, size):
    return list([lst[i:i + len(lst)//size] for i in range(0, len(lst), len(lst)//size)])

if __name__ == "__main__":
    pass