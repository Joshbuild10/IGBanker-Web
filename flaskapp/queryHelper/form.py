from flask import render_template

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

# Form validation for query page

def queryForm(form, info):
    # Get form data
    exam_board = form['board']
    subject = form['subject']
    filters = form.getlist('filter')
    search_terms = form.getlist('search_term')
    matches = form.getlist('match')

    # Validate exam board
    if exam_board not in info['boards']:
        raise ValidationError("Please select one of the supported exam boards from the dropdown")

    # Validate subject
    if subject not in info['subjects']:
        raise ValidationError("Please select one of the supported subjects from the dropdown")

    # Validate filter
    for filter  in filters:
        if filter not in info['filters']:
            raise ValidationError("Please select one of the valid filter from the dropdown")

    # Validate search strings
    for search_term in search_terms:
        if search_term == "":
            raise ValidationError("Please fill in all search strings")
    
    # Validate field lengths   
    if len(filters) != len(search_terms) != len(matches):
        raise ValidationError("Please fill in all fields")

    # Validate matches
    try:
        matches = [float(x) for x in matches]
        for match in matches:
            if match < 0 or match > 1:
                raise ValidationError("Please enter a decimal number between 0 and 1 for match")
    except ValueError:
        raise ValidationError("Please enter a decimal number between 0 and 1 for match")

    # If all valid, return data
    return exam_board, subject, filters, search_terms, matches