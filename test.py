from fuzzywuzzy import fuzz

str1 = "Riehen"
str2 = "Rieehn"

# Ratio gives a score out of 100, indicating how similar the strings are
similarity_score = fuzz.ratio(str1, str2)

print(similarity_score)  # Higher score means more similarity
