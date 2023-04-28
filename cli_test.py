import toml

print("hello world!")

print("\n\n======== TOML DEMO ========")
print("Here's how we can iterate through all the root directories using TOML!")

root_dir_args = toml.load("input/root_dir.toml")

for name, val in root_dir_args.items():
    print(name + " : " + val)

print("\nHere's how we can grab a specific thing through TOML!")
print("Q_ROOT: " + root_dir_args["Q_ROOT"])


print("\n======== IMPORT DEMO ========")
print("Here's how we can import! Notice that I use test_logic and that test_logic itself uses math_utils!")

from logic.test import test_logic
result = test_logic.perform_import_example(3)
print("result = " + str(result))
print ("We imported and used it correctly!")

