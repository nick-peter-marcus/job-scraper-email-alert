import re

def contains_words(input_string: str, search_words: list) -> bool:
    """ Checks whether a string contains specified key words
    Args: 
        input_string (str): The text to be searched in
        search_words (list): A list of words to be searched
    Returns:
        bool: True if any of the search_words appear in input_string.
    """
    re_search_terms = "|".join(search_words)
    matches = re.findall(re_search_terms, input_string.lower())
    return len(matches) > 0


def add_sorting_keys(jobs_dict: dict, pos_search_terms: list, neg_search_terms: list) -> dict:
    for job_details in jobs_dict.values():
        # initiate key - value pairs
        job_details['relevance'] = 0
        job_details['font_style'] = ''
        # overwrite default if job title contains relevant words
        if contains_words(job_details['title'], pos_search_terms):
            job_details['relevance'] = 1
            job_details['font_style'] = 'style="color:green;"'
        # overwrite default or positive relevance if negative terms are present
        if contains_words(job_details['title'], neg_search_terms):
            job_details['relevance'] = -1
            job_details['font_style'] = 'style="color:purple;"'
    return jobs_dict