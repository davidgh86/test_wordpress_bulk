import json

from tester import get_next_filename, get_first_matching_filename



if __name__ == "__main__":

    with open(get_first_matching_filename(), 'r', encoding='utf-8') as f:
        data = json.load(f)
        result = ""
        for matcher in data[0]["scheduler"]["matchers"]:
            if matcher["type"] == "operator":
                result += " " + matcher["value"]
            else:
                result += " ( " + matcher["type"] + " = " + str(matcher["value"]) + " )"
        print(result.strip())