
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    filter_horizontal = ('members',)

@admin.register(SharedNote)
class SharedNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    filter_horizontal = ('shared_with_teams', 'shared_with_users')
