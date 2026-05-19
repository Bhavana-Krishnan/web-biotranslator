from django.views.generic import CreateView, ListView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import DNAAnalysis
from .forms import DNAAnalysisForm
from Bio.Seq import Seq

class TranslateDNAView(CreateView):
    model = DNAAnalysis
    form_class = DNAAnalysisForm
    # fields = ['dna_sequence']
    template_name = 'biotranslator/index.html'
    success_url = reverse_lazy('DNA')

    def form_valid(self, form):
        raw_dna = form.cleaned_data['dna_sequence'].strip().upper()
    
        # Bio Calculations
        dna_obj = Seq(raw_dna)
        rna_seq = str(dna_obj.transcribe())
        
        # Keep codon translation clean to avoid Biopython warnings
        remainder = len(raw_dna) % 3
        trim_dna = raw_dna[:-remainder] if remainder != 0 else raw_dna
        protein_seq = str(Seq(trim_dna).translate())
        
        # Metrics
        g_count = raw_dna.count('G')
        c_count = raw_dna.count('C')
        total_bases = len(raw_dna)
        gc_pct = (g_count + c_count) / total_bases * 100 if total_bases > 0 else 0
        
        # Attach all the fields to the instance
        form.instance.dna_sequence = raw_dna
        form.instance.rna_sequence = rna_seq
        form.instance.protein_sequence = protein_seq
        form.instance.gc_content = round(gc_pct, 2)

        # Authenticate User check
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        else:                        
            form.instance.user = None

        # SAVE AND RENDER (Applies to both Guest and Logged-In Users)
        # By saving here and returning render_to_response, we avoid the 302 redirect completely
        self.object = form.save()
    
        context = self.get_context_data(
            form=form, 
            rna=rna_seq, 
            protein=protein_seq, 
            gc=round(gc_pct, 2),
            dna=raw_dna
        )
        return self.render_to_response(context)

class DNAHistoryListView(LoginRequiredMixin, ListView):
    model = DNAAnalysis
    template_name = 'biotranslator/history.html'
    context_object_name = 'history_items'

    def get_queryset(self):
        return DNAAnalysis.objects.filter(user=self.request.user).order_by('-created_at')


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Automatically redirects to login page after signing up
    template_name = 'registration/signup.html'