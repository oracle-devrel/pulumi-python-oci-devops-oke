import pulumi_random as random

# define a function to write an arn to a file
def write_to_file(str):
    f = open(".random.txt", "w")
    f.write(str)
    f.close()

class random_string:

   def create_random_string(self):
       random_string = random.RandomString("random_string",
                                                    length=6,
                                                    special="false")

       random_string.result.apply(lambda result: write_to_file(str=result))

   def fetch_random_string(self):
       return open(".random.txt", "r").read()


