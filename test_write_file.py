from functions.write_file import write_file

def run_tests():
    # Test Case 1
    res1 = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    print(res1)
    
    # Test Case 2
    res2 = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    print(res2)
    
    # Test Case 3
    res3 = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    print(res3)

if __name__ == "__main__":
    run_tests()