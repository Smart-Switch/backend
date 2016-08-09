from orator.migrations import Migration


class AddTokenToDevicesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('devices') as table:
            table.string('token')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('devices') as table:
            table.drop_column('token')
