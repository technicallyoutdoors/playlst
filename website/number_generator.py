# from a users post request, generate a random number that associates to a group
import random

group_code = random.randint(1000, 2000000)


print(group_code)

# todo make this more secure and make sure it's hashed so it cannot be hacked
