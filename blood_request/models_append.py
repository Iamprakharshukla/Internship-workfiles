
# --- Phase 17: Team Spaces & Knowledge Sharing ---

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SharedNote(models.Model):
    title = models.CharField(max_length=200, default="Untitled Note")
    content = CKEditor5Field(config_name='extends', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_with_teams = models.ManyToManyField(Team, related_name='shared_notes', blank=True)
    shared_with_users = models.ManyToManyField(User, related_name='received_notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
