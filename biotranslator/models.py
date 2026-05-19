from django.db import models
from django.contrib.auth.models import User

class DNAAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # The raw inputs and calculated outputs
    dna_sequence = models.TextField()
    rna_sequence = models.TextField()
    protein_sequence = models.TextField()
    gc_content = models.FloatField()
    
    # Automatically track when this calculation was made
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"