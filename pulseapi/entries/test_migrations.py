from utility.test_migrations import TestMigrations

class ModerationStateMigrationTestCase(TestMigrations):

    migrate_from = '0006_auto_20170525_2235'
    migrate_to = '0008_entry_moderation_state'

    def setUpBeforeMigration(self, apps):
        Entry = apps.get_model('entries', 'Entry')

        # Create an entry that should default to is_approved=False
        self.pending = Entry.objects.create(
            title = "pending",
            content_url = "http://example.com/pending"
        )

        # Create an entry that is explicitly is_approved=True
        self.approved = Entry.objects.create(
            title = "approved",
            content_url = "http://example.com/approved",
            is_approved = True
        )

    def test_moderation_state_migration(self):
        Entry = apps.get_model('entries', 'Entry')

        # default entries should have been moved over
        # to the "Pending" moderation state.
        pending = BlogPost.objects.get(title="pending")
        self.assertEqual(pending.moderation_state.name, "Pending")

        # approved entries should have been moved over
        # to the "Approved" moderation state
        approved = BlogPost.objects.get(title="approved")
        self.assertEqual(approved.moderation_state.name, "Approved")
