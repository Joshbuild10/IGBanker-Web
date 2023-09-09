import difflib
import os


# Function to query SQLite db 
def queryDb(db, parameters):

    # Initialize empty list for matches
    matches = []
    
    base_query = "SELECT * FROM questions WHERE exam_board = ? AND subject_code = ?"
    params = [parameters['exam_board'], parameters['subject_code']]

    # Gains the extra conditions to be queried
    extra_conditions = [(f" AND {condition['filter']} = ?", condition['search_term']) for condition in parameters['conditions']
                        if condition['filter'] != 'Text']

    params.extend([v for k,v in extra_conditions])
    full_query = base_query + "".join([k for k,v in extra_conditions])

    # Get rows from table 
    rows = [dict(zip(['Filename', 'Text'], row[-2:]))
                for row in db.execute(full_query, params).fetchall()]
    
    # Iterate to find rows that match the text conditions (if any)
    for row in rows:
        flag = 1
        for condition in parameters['conditions']:
            if condition['filter'] != 'Text':
                continue

            # Format search string
            search_term = condition['search_term'].upper().replace(' ', '')

            # Get the column value and its length
            column_value = row['Text']
            column_length = len(column_value)

            # Get the length of the search string
            search_length = len(search_term)
            max_similarity = 0

            # Loop through each possible starting position of a substring in the column value
            for i in range(column_length - search_length + 1):

                # Skips entries that doesn't have the first letter match
                if column_value[i] != search_term[0]:
                    continue

                # Get the substring of the column value that starts at position i and has the same length as the search string
                substring = column_value[i: i + search_length]

                # Calculate the similarity ratio between the substring and the search string
                similarity_ratio = difflib.SequenceMatcher(None, substring, search_term).ratio()
                max_similarity = max(max_similarity, similarity_ratio)

            # Check if the max similarity ratio is below the threshold and set the flag to 0
            if max_similarity < float(condition['match']):
                flag = 0
                break
        if flag:
            matches.append(row["Filename"].replace('\\', os.sep))
    return matches