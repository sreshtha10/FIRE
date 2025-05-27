# script to test fi-agent
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from fi_agent.agent import invoke_agent

file_contents=f"""
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    average = total / len(numbers)
    return average

def write_to_file(filename, data):
    f = open(filename, 'w')
    f.write("Average: " + data)
    f.close()

def main():
    nums = input("Enter numbers separated by commas: ")
    nums_list = nums.split(",")
    nums_list = [int(n) for n in nums_list]

    avg = calculate_average(nums_list)
    print("The average is: ", avg)

    write_to_file("average.txt", avg)

main()
"""

response = invoke_agent(file_contents=file_contents)
print(response)