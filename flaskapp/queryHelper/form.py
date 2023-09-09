from flask import render_template

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

# Form validation for query page

def queryForm(form, info):
    # Get form data
    exam_board = form['board']
    subject = form['subject']
    criteria = form.getlist('criteria')
    search_strings = form.getlist('search_string')
    similarities = form.getlist('similarity')

    # Validate exam board
    if exam_board not in info['boards']:
        raise ValidationError("Please select one of the supported exam boards from the dropdown")

    # Validate subject
    if subject not in info['subjects']:
        raise ValidationError("Please select one of the supported subjects from the dropdown")

    # Validate criteria
    for criterion in criteria:
        if criterion not in info['criterias']:
            raise ValidationError("Please select one of the valid criteria from the dropdown")

    # Validate search strings
    for search_string in search_strings:
        if search_string == "":
            raise ValidationError("Please fill in all search strings")
    
    # Validate field lengths   
    if len(criteria) != len(search_strings) != len(similarities):
        raise ValidationError("Please fill in all fields")

    # Validate similarities
    try:
        similarities = [float(x) for x in similarities]
        for similarity in similarities:
            if similarity < 0 or similarity > 1:
                raise ValidationError("Please enter a decimal number between 0 and 1 for similarity")
    except ValueError:
        raise ValidationError("Please enter a decimal number between 0 and 1 for similarity")

    # If all valid, return data
    return exam_board, subject, criteria, search_strings, similarities