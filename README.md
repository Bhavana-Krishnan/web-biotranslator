# # BioTranslator: DNA Analysis & Translation Platform

BioTranslator is a responsive, web-based bioinformatics application built with Django and Biopython. It provides users and researchers with an automated pipeline to process raw DNA sequences—either through text input or FASTA file uploads—and instantly transcribes them into RNA, translates them into protein sequences, and calculates key structural metrics like GC content.

The platform supports robust user session tracking, saving personal analysis histories for authenticated users while cleanly facilitating on-the-fly calculations for anonymous guests.

---
## Core Features

* **Dual Input Pipelines:** Supports direct plain-text sequence pasting or text-based FASTA/FA file uploads.
* **Automated Translation Pipeline:** Handles transcription (DNA to RNA) and translation (RNA to Protein) powered by Biopython.
* **Intelligent Codon Slicing:** Automatically detects and trims trailing partial codons (where length % 3 != 0) before translation to avoid truncation warnings.
* **Strict Sequence Validation:** Leverages Python set mathematics to sanitize inputs, stripping FASTA headers globally while filtering out non-nucleotide contaminants (A, T, C, G, N).
* **Stateful User Management:** Automatically maps saved records to logged-in user profiles while maintaining a seamless, zero-crash workflow for anonymous guests.
* **Optimized UX Rendering:** Overrides standard Post/Redirect/Get (PRG) constraints to dynamically render multi-variable translation contexts directly back to the active screen view.

---

## Tech Stack & Architecture

* **Backend Framework:** Django (Python)
* **Bioinformatics Core:** Biopython
* **Database Schema:** SQLite3 (Relational structure mapping user-to-analysis constraints via cascading Foreign Keys)
* **Frontend Interface:** Semantic HTML5, CSS3 Custom Variables, and Django Template Engine variables

---

## System Architecture & Code Blueprint

The following core modules drive the application's verification, calculation, and data-committal life cycle:

#### Models (`models.py`)

This file defines the database structure. It maps out the tables and columns where calculation records are stored.

```python
class DNAAnalysis(models.Model):
    # Links the analysis to a user. If the user deletes their account, this row is deleted too.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dna_sequence = models.TextField()
    rna_sequence = models.TextField()
    protein_sequence = models.TextField()
    gc_content = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
#### Forms (forms.py)
This handles input validation. It reads data from a file upload or the text input area, filters out FASTA header lines, and ensures the sequence contains only valid DNA bases.

```python
def clean(self):
    cleaned_data = super().clean()
    file = cleaned_data.get('file_upload')
    
    # 1. Extract the text sequence whether it is from a file or the text box
    if file:
        try:
            file_content = file.read().decode('utf-8').replace('\r', '')
            lines = file_content.split('\n')
            # Ignore lines starting with '>' (FASTA headers)
            sequence_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('>')]
            final_dna = "".join(sequence_lines).upper()
        except UnicodeDecodeError:
            self.add_error('file_upload', "Invalid file encoding. Please upload a plain text file.")
    else:
        final_dna = self.data.get('dna_sequence', '').strip().upper()

    # 2. Halt and throw an error if any illegal characters are found
    valid_bases = set('ATCGN')
    if set(final_dna) - valid_bases:
        self.add_error('dna_sequence', "Invalid characters found in sequence. DNA must only contain A, T, C, G, or N.")
        
    cleaned_data['dna_sequence'] = final_dna
    return cleaned_data
```

#### Views (views.py)
This runs the main business logic after the form passes validation. It processes the DNA sequence using Biopython, assigns the profile data if a user is logged in, saves the record, and prints the results back to the screen.

```python
def form_valid(self, form):
    raw_dna = form.cleaned_data['dna_sequence']
    
    # 1. Run the Biopython calculations
    dna_obj = Seq(raw_dna)
    rna_seq = str(dna_obj.transcribe())
    
    # Trim trailing partial characters so the translation engine doesn't throw warnings
    remainder = len(raw_dna) % 3
    trim_dna = raw_dna[:-remainder] if remainder != 0 else raw_dna
    protein_seq = str(Seq(trim_dna).translate())
    
    # 2. Pack the results into the database record instance
    form.instance.rna_sequence = rna_seq
    form.instance.protein_sequence = protein_seq
    
    # 3. Save to the database if the user is logged in, otherwise save as guest (None)
    if self.request.user.is_authenticated:
        form.instance.user = self.request.user
        
    self.object = form.save()
    
    # 4. Refresh the page context with the calculations instead of redirecting away
    return self.render_to_response(self.get_context_data(form=form, rna=rna_seq))

```
---

## 💻 Local Installation & Setup

Follow these steps to deploy and run the development environment locally:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/web_biotranslator.git
cd web_biotranslator

# 2. Create and activate a clean virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install core dependencies
pip install django biopython

# 4. Initialize database migrations
python manage.py makemigrations
python manage.py migrate

# 5. Launch the local development server
python manage.py runserver

```