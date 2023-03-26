import json, hashlib, statistics

FILENAME = "JSON FILE HERE"
KEY = "KEY NAME HERE"

with open(FILENAME, "r") as f:
    data = json.load(f)

test_sets = data[KEY]

res = {}

for length, test_results in test_sets.items():

    perm_count = test_results["permutation_count"]

    avg_runtimes_for_50p = []
    true_avg_runtimes = []

    for attempt in test_results["attempts"]:

        if not attempt["hash"] == hashlib.sha1(attempt["password"].encode()).hexdigest():
            print("Hash collision (I should never see this message)")
        
        percent = 100 * (attempt["index"] + 1) / perm_count

        avg_runtime = 50 * attempt["runtime"] / percent

        avg_runtimes_for_50p.append(avg_runtime)
        true_avg_runtimes.append(attempt["runtime"])
    
    print(f"{length} True Mean -> {statistics.mean(true_avg_runtimes)}")
    print(f"{length} Predicted Mean -> {statistics.mean(avg_runtimes_for_50p)}")
