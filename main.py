from flask import Flask, render_template, request, jsonify
import bibtexparser
import re
import json

app = Flask(__name__)

# Load the conference abbreviations from JSON
with open('sorted_abbreviations.json', 'r') as file:
    conference_abbreviations = json.load(file)

def find_conference_abbreviation(full_name):
    print(full_name)
    """Finds and returns the abbreviation for a given conference full name."""
    for abbreviation, names in conference_abbreviations.items():
        if any(name in full_name for name in names):
            return abbreviation.replace('_short', '')
    return full_name

def format_authors(authors):
    """Formats author names to ensure proper alignment and display."""
    authors = authors.replace('\n', ' ')
    author_list = authors.split(' and ')
    if len(author_list) > 1:
        indentation = ' ' * 20  # Alignment for subsequent lines of authors
        formatted_authors = (' and\n' + indentation).join(author_list)
    else:
        formatted_authors = authors
    return formatted_authors

def generate_new_id(entry):
    # Extract the first author's initials
    authors = entry.get('author', '').split(' and ')[0]
    initials = ''.join([name[0] for name in authors.split()[:2]])  # First two initials

    # Extract the first two letters of the first two significant words in the title
    title_words = re.findall(r'\b\w+', entry.get('title', ''))
    title_initials = ''.join(word[0] for word in title_words[:2])

    # Find the conference abbreviation and year
    id_field = entry.get('ID', '')
    if 'DBLP' in id_field:
        conference = id_field.split('/')[1]
    else:
        conference = find_conference_abbreviation(entry.get('booktitle', ''))
    year = entry.get('year', '')[2:4]

    # Combine all parts to form the new ID
    new_id = f"{initials.lower()}{title_initials.lower()}-{conference.lower()}-{year}"
    return new_id

def custom_format_entry(entry):
    """Formats a single BibTeX entry according to its type and the specified field order."""
    entry['ID'] = generate_new_id(entry)  # Update the ID with the new generated ID

    field_order = {
        'inproceedings': ['author', 'title', 'booktitle', 'pages', 'year'],
        'article': ['author', 'title', 'journal', 'volume', 'number', 'pages', 'year'],
    }

    entry_type = entry.get('ENTRYTYPE', '')
    ordered_fields = field_order.get(entry_type, list(entry.keys()))

    formatted_entry = "@{}{{{},\n".format(entry_type, entry['ID'])
    for field in ordered_fields:
        if field in entry:
            value = entry[field]
            if field == 'author':
                value = format_authors(value)
            if field == 'title':
                value = re.sub(r'\s+', ' ', value.replace('\n', ' '))
            if field in ['booktitle', 'journal']:
                value = find_conference_abbreviation(value)
                if field == 'booktitle':
                    value = f"Proceedings of {value}"
            formatted_entry += "    {} = {{{}}},\n".format(field, value)
    
    return formatted_entry.rstrip(',\n') + '\n}\n\n'

def format_bibtex_entry(bib_database):
    """Formats all entries in a BibTeX database."""
    formatted_entries = [custom_format_entry(entry) for entry in bib_database.entries]
    return ''.join(formatted_entries).strip('\n')

def simplify_bibtex(bibtex_str):
    """Simplifies and formats BibTeX entries provided as string."""
    bib_database = bibtexparser.loads(bibtex_str)
    for entry in bib_database.entries:
        for field in ['timestamp', 'doi', 'url', 'issn', 'editor']:
            entry.pop(field, None)  # Remove unwanted fields safely
    return format_bibtex_entry(bib_database)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Route to handle the main page requests."""
    if request.method == 'POST':
        bibtex_input = request.form['bibtex_input']
        simplified_bibtex = simplify_bibtex(bibtex_input)
        return jsonify({'simplified_bibtex': simplified_bibtex})
    return render_template('index.html')

@app.route('/load_default', methods=['GET'])
def load_default():
    """Route to load default BibTeX entries."""
    with open('default.bib', 'r') as file:
        default_bibtex = file.read()
    return jsonify({'default_bibtex': default_bibtex})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
