import hashlib, gc, string, random, time, json

print("\033[38;5;15m", end="\r")

# Typing variables so that the programmer doesn't descend into madness
from typing import List

# Symbols to use for testing
SYMBOLS = "~`!@#$%^&*()_-+=[]{}\\|;:'\",./<>?"

# Recursive worker used to generate permutation lists. It accepts the character list, the
# previous string which it should build off of, and the desired depth. When it reaches the
# target depth it will return a list of strings which will be added by upstream functions
# and returned as one giant list to our tests later
def recursive_worker(input_set: str, prev_chars: str, target_depth: int) -> List[str]:

    # List of all permutations from higher recursion depths to return to the parent function
    return_list = []

    if len(prev_chars) + 1 == target_depth:
        # We are at the final recursion depth, we do not need to spawn any more workers, so we
        # add the final permutations to the return list, one for each character in the input
        # set with the character at the end. Everything that is returned upstream originates
        # here
        for character in input_set:
            return_list.append(prev_chars + character)
    else:
        # We still need to go deeper recursively, so for each character in the input set
        # spawn a new worker with this worker's start string plus a character. This will
        # spawn one worker for each character in the input set
        for character in input_set:
            return_list += recursive_worker(input_set, prev_chars + character, target_depth)

    # Return the list, which will either be a set of final items if this is at the maximum
    # recursion depth, or a collection of all of the items returned from all of the
    # recursive workers which this instance spawned
    return return_list

# List generation function which creates every permutation of the input set of a certain length
# n by using a recursive worker function (found above)
def generate_permutations(input_set: List[str], target_length: int) -> List[str]:
    return recursive_worker(input_set, "", target_length)

# Function to perform one test
def run_test(test_id: int, input_set: str, target_length: int, test_count: int) -> dict:

    # Print statistics about the input set, target length, and test count
    print(f"Test #{test_id} -> \033[1;38;5;159m{input_set}\033[0;38;5;15m@\033[1;38;5;159m{target_length}\033[0;38;5;15m Count=\033[1;38;5;46m{test_count}\033[0;38;5;15m")

    # Generate permutation list which is every possible configuration of the input set to the
    # given length which is done before any brute forcing takes place
    attempt_list = generate_permutations(input_set, target_length)
    print(f"Successfully generated \033[1;38;5;226m{len(attempt_list):.3e}\033[0;38;5;15m permutations")

    # List to store dictionaries of each test result
    data_list = []

    for test in range(test_count):

        # Generate a random password of the target length and compute its hash so that we don't
        # use resources to generate the hash for each permutation
        correct_solution = "".join(random.choices(input_set, k=target_length))
        correct_solution_hash = hashlib.sha1(correct_solution.encode()).hexdigest()
        print(f"[ \033[1;38;5;159m{test + 1}\033[0;38;5;15m / \033[1;38;5;159m{test_count}\033[0;38;5;15m ] Attempting to brute password [\033[1;38;5;226m{correct_solution}\033[0;38;5;15m]", end="\r")

        # Note the start time using a benchmarking function
        start_time = time.perf_counter()

        # Loop through each attempt permutation that was previously generated
        for index, attempt in enumerate(attempt_list):

            # Perform the hash function using SHA256
            # Note for nerds: MD5 would be faster to use and more lightweight but because of major security
            # vulnerabilities found with it, its use is discontinued at any kind of scale or in production.
            attempt_hash = hashlib.sha1(attempt.encode()).hexdigest()

            # Perform the hash of the current permutation and check it against the saved 
            # password hash for our randomly generated test password
            if attempt_hash == correct_solution_hash:

                # Note the end time using a benchmarking function and display statistics
                end_time = time.perf_counter()
                print(f"[ \033[1;38;5;159m{test + 1}\033[0;38;5;15m / \033[1;38;5;159m{test_count}\033[0;38;5;15m ] Took \033[1;38;5;46m{round(end_time - start_time, 3)}\033[0;38;5;15m seconds to brute [\033[1;38;5;226m{correct_solution}\033[0;38;5;15m] - Item \033[1;38;5;50m{index}\033[0;38;5;15m/\033[1;38;5;50m{len(attempt_list)}\033[0;38;5;15m (\033[1;38;5;208m{round(100 * index / len(attempt_list), 2)}%\033[0;38;5;15m)")

                # Store the data which contains the password, the time in seconds that it
                # took to brute force the password, and where the randomly generated password 
                # fell within the list of possible permutations so that I can later account
                # for the random distribution within the list to find the true average time it
                # takes to brute force a password of a length N
                data_list.append({
                    "password": correct_solution, 
                    "hash": attempt_hash, 
                    "runtime": end_time - start_time,
                    "index": index
                })
                break

    attempt_list_length = len(attempt_list)

    # Delete the attempt list and manually run garbage collection
    del attempt_list
    
    # This process would already be executed after some time but we want to make sure that it runs 
    # before we begin initializing the next test.
    gc.collect()

    # Return data on the individual test set which contains the set of possible characters, 
    # the length which it was ran to, the number of tests run, the number of possible
    # permutations, and then the data from each individual test
    return {
        "input_set": input_set,
        "target_length": target_length,
        "test_count": test_count,
        "permutation_count": attempt_list_length,
        "attempts": data_list
    }

# Function to run a test set which takes the test ids (just for display purposes), the set
# of possible characters, the desired maximum password length, and the number of tests to
# run for each password length
def run_tests_on_input_set(ids: List[int], input_set: str, run_to_length: int, test_count: int) -> dict:

    return_data = {}

    # Loop from zero to the maximum length minus one
    for index in range(run_to_length):

        # The true length of the password is the index plus one because of zero-based
        # indexing
        true_length = index + 1

        # Set the return dictionary's value for the password length to the results of
        # the test which is run using the brute forcing function
        return_data[true_length] = run_test(ids[index], input_set, true_length, test_count)

    return return_data

# Perform each of the IA tests and add it to the dictionary by the name of the test -- this
# is the main driver code for the entire program
write_data = {
    "ascii_lowercase": run_tests_on_input_set([1, 2, 3, 4, 5], string.ascii_lowercase, 5, 100),
    "ascii_letters": run_tests_on_input_set([6, 7, 8, 9, 10], string.ascii_letters, 5, 100),
    "ascii_nosymbols": run_tests_on_input_set([11, 12, 13, 14], string.ascii_letters + string.digits, 4, 100),
    "ascii": run_tests_on_input_set([15, 16, 17, 18], string.ascii_letters + string.digits + SYMBOLS, 4, 100)
}

# Write the results to a file
with open("output.json", "w+") as f:
    json.dump(write_data, f, indent=4)

print("\033[0m", end="\r")
