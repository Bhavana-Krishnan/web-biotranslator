from django import forms
from .models import DNAAnalysis

class DNAAnalysisForm(forms.ModelForm):

    dna_sequence = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Paste your raw DNA sequence string here...',
            'rows': 5,
        })
    )
    # We add an optional file upload field that isn't saved directly to the DB
    file_upload = forms.FileField(
        required=False, 
        label="Or upload a file (.txt, .fasta)",
        widget=forms.ClearableFileInput(attrs={'accept': '.txt,.fasta,.fa'})
    )

    class Meta:
        model = DNAAnalysis
        fields = ['dna_sequence']
        widgets = {
            'dna_sequence': forms.Textarea(attrs={
                'placeholder': 'Paste your raw DNA sequence string here...',
                'rows': 5,
            }),
        }

    # Custom Validation Rule for the DNA sequence
    def clean_dna_sequence(self):
        # 1. Grab what the user typed or what was extracted from the file
        dna = self.cleaned_data.get('dna_sequence', '').strip().upper()
        
        if not dna:
            return dna

        # 2. Check for invalid characters
        valid_bases = set('ATCGN')  # Including 'N' for unknown/ambiguous bases common in sequencing
        invalid_chars = set(dna) - valid_bases
        
        if invalid_chars:
            # This halts form submission and sends an error message back to the user
            raise forms.ValidationError(
                f"Invalid characters found in sequence: {', '.join(invalid_chars)}. "
                "DNA must only contain A, T, C, G (or N)."
            )
            
        return dna

    # Clean the whole form to coordinate file upload parsing
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file_upload')
        # dna_sequence = cleaned_data.get('dna_sequence')

        # # If a file is uploaded, read it and overwrite/populate the dna_sequence field
        # if file:
        #     try:
        #         # Read file, replace carriage returns, and split by newline
        #         file_content = file.read().decode('utf-8').replace('\r', '')
        #         lines = file_content.split('\n')
                
        #         # Strip out any line starting with '>' (FASTA headers)
        #         sequence_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('>')]
        #         parsed_dna = "".join(sequence_lines).upper()

        #         if not parsed_dna:
        #             raise forms.ValidationError("The uploaded file appears to be empty.")

        #         # Force this parsed string into our dna_sequence field
        #         cleaned_data['dna_sequence'] = parsed_dna
                
        #     except UnicodeDecodeError:
        #         raise forms.ValidationError("Could not decode file. Please upload a plain text or text-based FASTA file.")
        
        # elif not dna_sequence:
        #     raise forms.ValidationError("Please either paste a sequence or upload a file.")

        # return cleaned_data
        final_dna = ""

        if file:
            try:
                # User uploaded a file -> extract text and clean FASTA headers
                file_content = file.read().decode('utf-8').replace('\r', '')
                lines = file_content.split('\n')
                sequence_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('>')]
                final_dna = "".join(sequence_lines).upper()

                if not final_dna:
                    self.add_error('file_upload', "The uploaded file appears to be empty or contains only headers.")
                    return cleaned_data
            except UnicodeDecodeError:
                self.add_error('file_upload', "Could not decode file. Please upload a plain text or text-based FASTA file.")
                return cleaned_data
        else:
            # No file uploaded -> grab whatever the user pasted into the textbox
            # We look at self.data directly because Django clears empty fields from cleaned_data early on
            final_dna = self.data.get('dna_sequence', '').strip().upper()

        # 2. Check if both inputs are completely missing
        if not final_dna:
            self.add_error('dna_sequence', "Please either paste a sequence or upload a file.")
            return cleaned_data

        # 3. Security Checkpoint: Character Validation
        valid_bases = set('ATCGN')
        invalid_chars = set(final_dna) - valid_bases
        
        if invalid_chars:
            # Highlights the exact field causing trouble with a specific error message
            self.add_error('dna_sequence', f"Invalid characters found in sequence: {', '.join(invalid_chars)}. DNA must only contain A, T, C, G (or N).")
            return cleaned_data

        # 4. Success! Save the final sequence string so the view can read it
        cleaned_data['dna_sequence'] = final_dna
        return cleaned_data